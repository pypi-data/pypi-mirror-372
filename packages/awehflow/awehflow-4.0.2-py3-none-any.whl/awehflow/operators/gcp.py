from typing import Optional
import re
import os
from pyhocon import ConfigFactory
from typing import TYPE_CHECKING, Sequence

from airflow import configuration
from airflow.version import version as airflow_version
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.exceptions import AirflowException
from airflow.models.baseoperator import BaseOperator
from airflow.models.skipmixin import SkipMixin
from airflow.utils.decorators import apply_defaults
from google.cloud.bigquery import SchemaField

from typing import Iterable

from awehflow.operators.flow import EventEmittingOperator
from awehflow.utils import utc_now
import time

class BigQueryJobExecutionOperator(BigQueryInsertJobOperator):
    """
    A custom Airflow operator that uses the BigQueryInsertJobOperator to insert a bigquery job and the insert_job method to execute a cleanup query if specified.
    If a cleanup query is specified please specify a destination table. This operator can be used in deferrable mode.

    :param destination_dataset_table: The table in BigQuery that will be changed, used to check whether table exists before executing cleanup query.
    :type destination_dataset_table: str
    :param cleanup_query_configuration: A dictionary specifying the bigquery job to be executed for the cleanup query, this dictionary maps directly to BigQuery's
    configuration field in the job object. For more details see https://cloud.google.com/bigquery/docs/reference/rest/v2/Job#jobconfiguration.
    :type cleanup_query_configuration: dict
    :param configuration: A dictionary specifying the bigquery job to be executed, this dictionary maps directly to BigQuery's configuration field in the job object.
    :type configuration: dict
    :param gcp_conn_id: The connection ID to use when connecting to Google Cloud Platform.
    :type gcp_conn_id: str
    """
    
    template_fields = ('destination_dataset_table', 'configuration', 'cleanup_query_configuration', 'job_id', 'impersonation_chain', 'project_id')

    def __init__(
        self,
        cleanup_query_configuration: dict = None, # type: ignore
        destination_dataset_table: str = None, # type: ignore
        *args,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.cleanup_query_configuration = cleanup_query_configuration
        self.destination_dataset_table = destination_dataset_table

    def execute(self, context):

        if self.cleanup_query_configuration:
            hook_kwargs=dict()
            hook_kwargs['gcp_conn_id'] = self.gcp_conn_id
            hook_kwargs['location'] = self.location

            if int(re.sub('[^0-9]', '', airflow_version)) < 240: # pragma: no cover
                hook_kwargs['delegate_to'] = self.delegate_to # type: ignore
            else:
                hook_kwargs['impersonation_chain'] = self.impersonation_chain

            self.hook = BigQueryHook(
                **hook_kwargs
            )
            credentials = self.hook.get_credentials()
            credential_email = credentials.service_account_email # type: ignore
            self.log.info(f"Created BigQueryHook with account: {credential_email}")
            if self.destination_dataset_table == None:
                raise ValueError('No destination_dataset_table was given, if a cleanup query was provided please set a destination_dataset_table in the following format: project_id.dataset_id.table_id')
            
            replaced_destination_dataset_table = self.destination_dataset_table.replace(':', '.')
            split_destination_dataset_table = replaced_destination_dataset_table.split(".")

            if len(split_destination_dataset_table) != 3:
                raise ValueError('Please set a destination_dataset_table in the following format: project_id.dataset_id.table_id')
        
            project_id = split_destination_dataset_table[0]
            dataset_id = split_destination_dataset_table[1]
            table_id = split_destination_dataset_table[2]

            self.log.info('Checking if table exist: {}.{}.{}'.format(project_id, dataset_id, table_id))
            
            if self.hook.table_exists(project_id=project_id, dataset_id=dataset_id, table_id=table_id):
                self.log.info('Table exists')
                self.log.info('Executing cleanup query: {}'.format(self.cleanup_query_configuration['query']['query']))

                cleanup_job_id = self.hook.insert_job(configuration = self.cleanup_query_configuration)
            
                qj = self.hook.get_job(job_id=cleanup_job_id)
                while not qj.done():
                    self.log.info(f'Waiting for job [{cleanup_job_id}] to complete...')
                    time.sleep(1)

                self.log.info('Completed execution of cleanup query')   

        
        self.log.info(f"The full job configuration is {self.configuration}")
        job_id = super().execute(context)
        return job_id


class BigQueryJobTaskMetricOperator(EventEmittingOperator):
    """
    Neeeds help
    """

    @apply_defaults
    def __init__(
            self,
            task_ids: list=[],
            xcom_key: str='return_value',
            bigquery_conn_id: str=None, # type: ignore
            gcp_conn_id: str='google_cloud_default',
            *args, **kwargs):
        """
        :param task_ids: List of task_ids saying which tasks to sink their job_metrics for
        :param xcom_key: XCOM key used to pull the bigquery job id from the specified tasks
        """
        self.task_ids = task_ids
        self.xcom_key = xcom_key
        self.gcp_conn_id = gcp_conn_id
        if bigquery_conn_id:
            self.gcp_conn_id = bigquery_conn_id

        super(BigQueryJobTaskMetricOperator, self).__init__(*args, **kwargs)


    def execute(self, context):
        if int(re.sub('[^0-9]', '', airflow_version)) < 220: # pragma: no cover
            next_execution_date = context['next_execution_date']
        else:
            next_execution_date = context['data_interval_end']
    
        hook = BigQueryHook(
            gcp_conn_id=self.gcp_conn_id
        )
        credentials = hook.get_credentials()
        credential_email = credentials.service_account_email # type: ignore
        self.log.info(f"Created BigQueryHook with account: {credential_email}")

        client = hook.get_client(project_id=hook.project_id)

        for task_id in self.task_ids:
            job_id = context['task_instance'].xcom_pull(key=self.xcom_key, task_ids=task_id)

            if isinstance(job_id, str):
                job_id = [job_id]

            if job_id:
                for jid in job_id:
                    job = client.get_job(
                        job_id=jid
                    )
                    self.emit_event('task_metric', {
                        'run_id': context['dag_run'].run_id,
                        'dag_id': self.dag.dag_id,
                        'job_name': context['task'].params.get('job_name', ''),
                        'task_id': task_id,
                        'value': job._properties,
                        'created_time': utc_now(),
                        'reference_time': next_execution_date
                    })


class BigQueryShortCircuitOperator(BaseOperator, SkipMixin):
    """
    A "short circuit" operator that can be used a a "pre check" system.  The supplied sql statement should turn a single BOOL column.

    If the BOOL value is TRUE then downstream processors will execute as normal.
    If the BOOL value is FALSE then any downstream processors will be skipped.

    """

    template_fields = ('sql',)
    template_ext = ('.sql',)

    @apply_defaults
    def __init__(
            self,
            sql: str,
            gcp_conn_id: str='google_cloud_default',
            bigquery_conn_id: str=None, # type: ignore
            use_legacy_sql: bool=True,
            *args, **kwargs):
        
        self.sql = sql
        self.gcp_conn_id = gcp_conn_id
        if bigquery_conn_id:
            self.gcp_conn_id = bigquery_conn_id
        self.use_legacy_sql = use_legacy_sql

        super(BigQueryShortCircuitOperator, self).__init__(*args, **kwargs)


    def execute(self, context):
        records = self.db_hook.get_first(self.sql)
        success = records and all([bool(r) for r in records])

        if success:
            return

        self.log.info('Skipping downstream tasks...')

        downstream_tasks = context['task'].get_flat_relatives(upstream=False)
        self.log.debug("Downstream task_ids %s", downstream_tasks)

        if downstream_tasks:
            self.skip(context['dag_run'], context['ti'].execution_date, downstream_tasks)

        self.log.info("Done.")

    @property
    def db_hook(self):
        hook = BigQueryHook(gcp_conn_id=self.gcp_conn_id, use_legacy_sql=self.use_legacy_sql)
        credentials = hook.get_credentials()
        credential_email = credentials.service_account_email # type: ignore
        self.log.info(f"Created BigQueryHook with account: {credential_email}")
        return hook


class BigQueryPushFirstResultToXComOperator(BaseOperator):
    """Execute a SQL query and push the 1st result record to xcom for use by other tasks

    Raises:
        Exception: If the query does not return any result

    Returns:
        _type_: The 1st record returned by the query, which will be pushed to xcom
    """
    template_fields: Sequence[str] = (
        "sql",
    )

    template_ext: Sequence[str] = (
        ".sql",
    )
    @apply_defaults
    def __init__(
            self,
            sql,
            gcp_conn_id: str='gcp_default',
            bigquery_conn_id: Optional[str] = None,
            use_legacy_sql=True,
            *args, **kwargs):
        """
        :param sql: Source table name that has been materialized (:project_id.:dataset_id.:table_name)
        :param use_legacy_sql: Whether to execute the query in legacy SQL mode or not
        """
        if bigquery_conn_id:
            gcp_conn_id = bigquery_conn_id

        super(BigQueryPushFirstResultToXComOperator, self).__init__(*args, **kwargs)
        self.sql = sql
        self.use_legacy_sql = use_legacy_sql
        self.gcp_conn_id = gcp_conn_id

    def execute(self, context):
        hook = BigQueryHook(gcp_conn_id=self.gcp_conn_id, use_legacy_sql=self.use_legacy_sql)
        result = hook.get_first(self.sql)
        if not result:
            raise Exception("No materialized date found")
        return result


class BigQueryUpdateTableDescriptionOperator(BaseOperator):
    template_fields: Sequence[str] = (
                        'destination_dataset_tables', 
                       'description_data', 
                       'source_table')
    
    # template_ext: Sequence[str] = ('.conf', '.hocon', )
    """
    A custom Airflow operator that uses the BigQueryHook to update the schema of a BigQuery table based on
    one of two sources.

    source_table - The column descriptions are read from the source table and applied to the list of destination tables
    description_data - The column descriptions are loaded as a HOCON configuration with key-value pairs to provide the
    column_name and column_description. This can either be HOCON text or a reference to a hocon file with extension .conf or .hocon

    :param destination_dataset_tables: The tables in BigQuery to update with descriptions.
    :type destination_dataset_tables: list
    :param description_data: The path to a file containing description data. Path given from INSIDE dags directory.
    :type description_data: str
    :param source_table: The ID of the table containing original descriptions to update new tables with.
    :type source_table: str
    :param descriptions_compulsory: A boolean indicator whether ALL fields require a description or the process will stop.
    :type descriptions_compulsory: bool
    :param gcp_conn_id: The connection ID to use when connecting to Google Cloud Platform.
    :type gcp_conn_id: str
    """

    @apply_defaults
    def __init__(
        self,
        destination_dataset_tables: list = [],
        description_data: str = None, # type: ignore
        source_table: str = None, # type: ignore
        descriptions_compulsory: bool = False,
        gcp_conn_id: str = 'gcp_default',
        *args,
        **kwargs
    ):
        super(BigQueryUpdateTableDescriptionOperator, self).__init__(*args, **kwargs)
        self.gcp_conn_id = gcp_conn_id
        if isinstance(destination_dataset_tables, str):
            self.destination_dataset_tables = [destination_dataset_tables]
        else:
            self.destination_dataset_tables = destination_dataset_tables
        self.description_data = description_data
        self.source_table = source_table
        self.descriptions_compulsory = descriptions_compulsory
        self.hook = None


    def update_descriptions(self, new_schema: list, table_resource: str):
        project_id, dataset_id, table_id = table_resource.split('.')
        self.bq_hook.update_table_schema(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id,
            include_policy_tags=True,
            schema_fields_updates=new_schema,
        )


    def bq_table_exist_check(self, table_resource: str):
        self.log.info(f'Checking if {table_resource} exists in BigQuery')
        project_id, dataset_id, table_id = table_resource.split('.')
        tbl_exist = self.bq_hook.table_exists(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id
        )
        if tbl_exist is False:
            raise AirflowException(f'{table_resource} not found in BigQuery. Stopping process. Set destination_dataset_tables in the following format: project_id.dataset_id.table_id')


    def get_schema_bq(self, table_resource: str):
        project_id, dataset_id, table_id = table_resource.split('.')
        schema_dict = self.bq_hook.get_schema(
            project_id=project_id,
            dataset_id=dataset_id,
            table_id=table_id
        )
        schema = schema_dict['fields']
        return schema
    
    
    def update_description_data(self, dest_schema: list, description_dict: dict) -> list:
        for fld in dest_schema:
            fld_lower = str(fld["name"]).lower()

            if fld_lower in description_dict:
                fld['description'] = description_dict[fld_lower]
            elif self.descriptions_compulsory is True:
                raise AirflowException(f'Field: {fld["name"]} not found in config. Stopping process as all fields require descriptions')
        
        return dest_schema
    

    def get_cleaned_schema_data(self):
        lower_desc_data = self.description_data.lower()
        desc_data = {}
        if lower_desc_data.endswith('.conf') or lower_desc_data.endswith('hocon'):
            dags_path = os.path.join(configuration.conf.get('core', 'dags_folder'), self.description_data)
            desc_data = ConfigFactory.parse_file(dags_path)
        else:
            desc_data = ConfigFactory.parse_string(self.description_data)

        cleaned_descriptions = {}

        for key in desc_data.keys():
            cleaned_descriptions[key.lower()] = desc_data.get(key=key)

        return cleaned_descriptions
    

    def execute(self, context):
        if self.destination_dataset_tables == []:
            raise AirflowException('No tables to update schema')
  
        # Use source table in bq to update tables (default)
        if self.source_table:
            self.bq_table_exist_check(self.source_table)
            self.log.info('Using source table to update schema(s) in BigQuery')
            schema = self.get_schema_bq(self.source_table)
            for table in self.destination_dataset_tables:
                self.bq_table_exist_check(table)
                self.update_descriptions(schema, table)
        # Use config data to update tables 
        elif self.description_data:
            description_dict = self.get_cleaned_schema_data()
            for table in self.destination_dataset_tables:
                self.bq_table_exist_check(table)
                dest_schema = self.get_schema_bq(table)
                new_schema = self.update_description_data(dest_schema=dest_schema, description_dict=description_dict)
                self.update_descriptions(new_schema=new_schema, table_resource=table)
        else:
            raise AirflowException('No source table or config with descriptions found. Stopping process')
        
    @property
    def bq_hook(self) -> BigQueryHook:
        if self.hook == None:
            self.hook = BigQueryHook(gcp_conn_id=self.gcp_conn_id)
            credentials = self.hook.get_credentials()
            credential_email = credentials.service_account_email # type: ignore
            self.log.info(f"Created BigQueryHook with account: {credential_email}")
        return self.hook
