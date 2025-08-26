import copy
import datetime

import pendulum
from dotty_dict import Dotty

from awehflow.utils import merge_dicts


class Config(Dotty):
    DEFAULTS = {
        'name': None,
        'version': 1,
        'description': None,
        'owner': 'airflow',
        'start_date': None,
        'end_date': None,
        'schedule': None,
        'catchup': False,
        'timezone': 'Africa/Johannesburg',
        'engineers': [],
        'alert_on': [],
        'params': {},
        'pre_hooks': [],
        'dependencies': [],
        'tasks': [],
        'default_dag_args': {}
    }

    REQUIRED = [
        'name', 'tasks'
    ]

    def __init__(self, config_dict, environment='dev', dag_id_prefix=''):
        config = merge_dicts(copy.deepcopy(self.DEFAULTS), config_dict)

        for field in self.REQUIRED:
            if not config.get(field):
                raise Exception('{} required'.format(field))

        config['dag_id'] = "{}{}_v{}".format(dag_id_prefix, config['name'], config['version'])
        config['start_date'] = self.__get_datetime_obj(config.get('start_date'), config.get('timezone'))
        config['end_date'] = self.__get_datetime_obj(config.get('end_date'), config.get('timezone'))
        config['params'] = self.__apply_environment_to_params(environment, config.get('params'))

        super(Config, self).__init__(config)

    @staticmethod
    def __apply_environment_to_params(environment, params):
        tmp_params = copy.deepcopy(params.get('default', {}))
        if environment in params:
            tmp_params = merge_dicts(tmp_params, params.get(environment))
        return tmp_params

    @staticmethod
    def __get_datetime_obj(date_string, timezone):
        if not date_string:
            return None
        return datetime.datetime.strptime(date_string, '%Y-%m-%d').replace(tzinfo=pendulum.timezone(timezone))
