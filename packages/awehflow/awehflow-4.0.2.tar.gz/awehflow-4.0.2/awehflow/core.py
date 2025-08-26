import glob
import json
import os
from pyhocon import ConfigFactory

import pendulum
from pendulum import timezone as pd_tz

import yaml
import re
from airflow.version import version as airflow_version
from airflow.models.dag import DAG
from airflow.configuration import conf as airflow_config
from airflow.utils.trigger_rule import TriggerRule
from jinja2.utils import import_string

from awehflow.config import Config
from awehflow.events.alerts import AlertsEventHandler
from awehflow.operators.flow import StartOperator
from awehflow.operators.flow import SuccessOperator
from awehflow.operators.flow import FailureOperator
from awehflow.operators.flow import EventEmittingOperator
from awehflow.utils import uniquify_name
from awehflow.utils import merge_dicts


class ConfigCache:
    def __init__(self, configs_path):
        self.configs_path = configs_path

    @property
    def cache_directory_path(self):
        return os.path.join(self.configs_path, '.cache')

    @property
    def bundle_path(self):
        return os.path.join(self.cache_directory_path, 'configs_bundle.json')

    @property
    def config_files_glob(self):
        yaml_files = glob.glob(os.path.join(self.configs_path, '**', '*.yml'), recursive=True)
        hocon_files = glob.glob(os.path.join(self.configs_path, '**', '*.hocon'), recursive=True)

        return yaml_files + hocon_files

    def refresh_cache(self):
        """Before deploying to Airflow, always refresh the cache, then sync the bundle to the live Airflow instance"""

        if not os.path.exists(self.cache_directory_path):
            os.makedirs(self.cache_directory_path)

        if os.path.isfile(self.bundle_path): #pragma: no cover
            os.remove(self.bundle_path)

        configs = []
        for file_path in self.config_files_glob:
            file_ext = file_path[file_path.rindex('.'):].lower()
            if file_ext == '.yml':
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif file_ext == '.hocon':
                data = dict(ConfigFactory.parse_file(file_path))
            else: #pragma: no cover
                raise Exception(f"File extension [{file_ext}] not supported")

            # Cache only configs that are 'valid'
            valid_config = True
            for conf in Config.REQUIRED:
                if not conf in data:
                    valid_config = False
            
            if valid_config:
                configs.append(data)
            else:
                print(f'ERROR: Config file [{file_path}] does not have required fields: {Config.REQUIRED}')

        with open(self.bundle_path, 'w') as fp:
            json.dump(configs, fp, indent=4)

    def read_cache(self, environment='dev', dag_id_prefix=''):
        if not os.path.exists(self.bundle_path):
            raise FileNotFoundError('Configs cache bundle json file not found')

        with open(self.bundle_path) as json_file:
            configs = json.load(json_file)

        return [Config(config_dict=config, environment=environment, dag_id_prefix=dag_id_prefix) for config in configs]


class DagLoader:
    """Parses pipeline configurations, creates Airflow DAGs and exposes them for Airflow to pickup"""

    def __init__(self, project, configs_path, dag_id_prefix='', event_handlers=None, alerters=None, environment='dev'):
        """
        :param project: Name of the project (e.g. name of repo where instance is instanciated)
        :param configs_path: Full path to folder where config files are located
        :param dag_id_prefix: prefix every dag_id with this
        :param event_handlers: List of EventHandler instances
        :param alerters: List of Alerter instances
        :param environment: prod/dev
        """
        self.project = project
        self.configs_path = configs_path
        self.dag_id_prefix = dag_id_prefix
        self.configs_cache = ConfigCache(configs_path=configs_path)
        self.event_handlers = event_handlers or []
        self.alerters = alerters or []
        self.environment = environment

    def load(self, global_symbol_table):
        configs = self.configs_cache.read_cache(environment=self.environment, dag_id_prefix=self.dag_id_prefix)
        dags = []
        for config in configs:
            variable_name = uniquify_name(config.get('name'))
            dag = self.__build_dag(config)
            dags.append((variable_name, dag))
            global_symbol_table[variable_name] = dag

        return dags

    def __get_dag_event_handlers(self, config: Config):
        event_handlers = self.event_handlers.copy()
        event_handlers.append(AlertsEventHandler(alerters=self.alerters, alert_on=config.get('alert_on')))
        return event_handlers

    def __build_dag(self, config: Config) -> DAG:
        event_handlers = self.__get_dag_event_handlers(config)

        default_dag_args = merge_dicts({
            'owner': config.get('owner'),
            'project': self.project,
            'start_date': config.get('start_date'),
            'end_date': config.get('end_date'),
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 0,
            'on_failure_callback': self.generate_on_failure_callback(config, event_handlers)
        }, config.get('default_dag_args'))

        local_airflow_version = int(re.sub('[^0-9]', '', airflow_version))

        concurrency_default = None
        if local_airflow_version < 220:
            concurrency_default = airflow_config.getint('core', 'dag_concurrency')
        else:
            concurrency_default = airflow_config.getint('core', 'max_active_tasks_per_dag')

        dag_kwargs = dict()
        dag_kwargs['dag_id'] = config.get('dag_id') # type: ignore
        dag_kwargs['description'] = config.get('description')
        dag_kwargs['schedule_interval'] = config.get('schedule')
        dag_kwargs['catchup'] = config.get('catchup', False)
        dag_kwargs['template_searchpath'] = self.configs_path
        dag_kwargs['user_defined_macros'] = self.generate_user_defined_macros(config)
        dag_kwargs['default_args'] = default_dag_args
        dag_kwargs['concurrency'] = config.get('concurrency', config.get('dag_concurrency', concurrency_default)) # type: ignore
        
        if local_airflow_version >= 220:
            dag_kwargs['max_active_tasks'] = config.get('max_active_tasks', airflow_config.getint('core', 'max_active_tasks_per_dag'))
        
        dag_kwargs['max_active_runs'] = config.get('max_active_runs', airflow_config.getint('core', 'max_active_runs_per_dag'))
        dag_kwargs['dagrun_timeout'] = config.get('dagrun_timeout', None)
        dag_kwargs['doc_md'] = config.get('doc_md', None)
        dag_kwargs['access_control'] = config.get('access_control', None)
        dag_kwargs['is_paused_upon_creation'] = config.get('is_paused_upon_creation', None)
        dag_kwargs['tags'] = config.get('tags', None)

        # Load params for DAG trigger window
        dag_kwargs['params'] = config.get('dag_params', None)

        dag = DAG(**dag_kwargs)

        start = StartOperator(
            task_id='start',
            dag=dag,
            project=self.project,
            job_name=config.get('name'),
            engineers=config.get('engineers'),
            event_handlers=event_handlers
        )

        pre_hook_configs = config.get('pre_hooks', [])
        if pre_hook_configs:
            pre_hooks = DependencySensors(
                task_configs=pre_hook_configs,
                dag=dag,
                params=config.get('params')
            )

            for pre_hook in pre_hooks.leaves:
                pre_hook >> start

        tasks = TasksSubDag(
            task_configs=config.get('tasks'),
            dag=dag,
            job_name=config.get('name'),
            params=config.get('params'),
            event_handlers=event_handlers
        )

        dependency_configs = config.get('dependencies', [])
        if dependency_configs:
            dependencies = DependencySensors(
                task_configs=dependency_configs,
                dag=dag,
                params=config.get('params')
            )

            for dependency_check in dependencies.roots:
                start >> dependency_check

            for dependency_check in dependencies.leaves:
                dependency_check >> tasks.roots
        else:
            start >> tasks.roots

        success = SuccessOperator(
            task_id='success',
            dag=dag,
            project=self.project,
            job_name=config.get('name'),
            engineers=config.get('engineers'),
            trigger_rule=TriggerRule.NONE_FAILED,
            event_handlers=event_handlers
        )

        tasks.leaves >> success

        return dag

    def generate_on_failure_callback(self, config, event_handlers):
        def on_failure_callback(context):
            failure = FailureOperator(
                task_id='failure',
                dag=context.get('dag'),
                project=self.project,
                job_name=config.get('name'),
                engineers=config.get('engineers'),
                event_handlers=event_handlers
            )
            return failure.execute(context=context)
        return on_failure_callback

    @staticmethod
    def generate_user_defined_macros(config):
        return {
            'tz_aware': lambda ds: ds.astimezone(pd_tz(config.get('timezone'))).strftime('%Y-%m-%d'),
            'tz_aware_nodash': lambda ds: ds.astimezone(pd_tz(config.get('timezone'))).strftime('%Y%m%d')
        }

    @staticmethod
    def build_task(task_id, dag, operator, params=None, expected_class=None, event_handlers=None, **kwargs):
        operator_class = import_string(operator)
        if expected_class and not issubclass(operator_class, expected_class): # type: ignore
            raise Exception("Unexpected operator class. Expected {}, got {}".format(expected_class.__name__,
                                                                                    operator_class.__name__))
        obj = operator_class(task_id=task_id, dag=dag, params=(params or {}), **kwargs) # type: ignore
        if event_handlers and isinstance(obj, EventEmittingOperator):
            obj.event_handlers = event_handlers
        return obj


class SubDag:
    """Builds and loads configured sub DAG into parent DAG"""

    def __init__(self, task_configs, dag, params, event_handlers=None):
        self.tasks = {}
        self.dag = dag
        self.__build_sub_dag(task_configs, params, event_handlers)

    @property
    def leaves(self):
        """Tasks with no children. Last to execute"""
        return [self.tasks[task_id] for task_id in self.cached_leaf_ids]

    @property
    def roots(self):
        """Tasks with no parents. First to execute"""
        return [self.tasks[task_id] for task_id in self.cached_root_ids]

    def __build_sub_dag(self, task_configs, params, event_handlers):
        """
        Instantiate all tasks first,
        then set up dependencies
        """

        for task_config in task_configs:
            task_kwargs = task_config.get('params', {})
            task_params = params

            if 'params' in task_kwargs:
                task_params = merge_dicts(task_params, task_kwargs['params'])
                del task_kwargs['params']

            task = DagLoader.build_task(
                task_id=task_config.get('id'),
                dag=self.dag,
                operator=task_config.get('operator'),
                params=params,
                event_handlers=event_handlers,
                **task_kwargs
            )
            self.tasks[task.task_id] = task

        for task_config in task_configs:
            upstream = task_config.get('upstream', [])
            downstream = task_config.get('downstream', [])

            for task_id in upstream:
                if task_id in self.tasks:
                    self.tasks[task_config.get('id')] << self.tasks[task_id]

            for task_id in downstream:
                if task_id in self.tasks:
                    self.tasks[task_config.get('id')] >> self.tasks[task_id]

        # Cache leaves and roots. This is necessary since any new dependency being set
        # changes the downstream_list or upstream_list of the tasks
        self.cached_leaf_ids = [task.task_id for task in self.tasks.values() if not task.downstream_list]
        self.cached_root_ids = [task.task_id for task in self.tasks.values() if not task.upstream_list]


class TasksSubDag(SubDag):
    """Builds and loads configured tasks into DAG"""

    def __init__(self, task_configs, dag, job_name, params, event_handlers=None):
        enriched_params = merge_dicts({'job_name': job_name}, params)
        super(TasksSubDag, self).__init__(task_configs, dag, enriched_params, event_handlers)


class DependencySensors(SubDag):
    """Builds and loads configured dependency sensors into DAG"""

    def enrich_dict(self, task_config):
        if 'sensor' in task_config.get('operator').lower():
            return merge_dicts({'params': {'timeout': 0}}, task_config)
        return task_config

    def __init__(self, task_configs, dag, params):
        enriched_task_configs = [self.enrich_dict(task_config) for task_config in task_configs]
        super(DependencySensors, self).__init__(enriched_task_configs, dag, params)
