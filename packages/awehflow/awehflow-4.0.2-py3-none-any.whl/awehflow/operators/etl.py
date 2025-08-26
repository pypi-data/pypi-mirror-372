from airflow.models.baseoperator import BaseOperator
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException
from airflow.utils.decorators import apply_defaults
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

class SQLToSQLOperator(BaseOperator):
    """
    Executes BigQuery SQL queries in a specific BigQuery database

    :param sql: the sql code to be executed (templated)
    :type sql: Can receive a str representing a sql statement,
        a list of str (sql statements), or reference to a template file.
        Template reference are recognized by str ending in '.sql'.
    :param src_conn_id: reference to a source data connection hook.
    :type src_conn_id: str
    :param src_hook_config: a dictionary of properties to apply to the source connection hook. IE {'use_legacy_sql': True}
    :type src_hook_config: dict
    :param cleanup_query: a sql query which will be executed prior to inserting records, this can be used to guarantee idempotency
    :type cleanup_query: str
    :param dest_conn_id: reference to the destination sql database hook. Supported hooks are ['postgres']
    :type dest_conn_id: str
    :param dest_hook_config: a dictionary of properties to apply to the destination connection hook. IE {'use_legacy_sql': False}
    :type dest_hook_config: dict
    :param dest_schema: a db schema name where the destination table resides. Default public
    :type dest_schema: str
    :param dest_table: a table matching the data and schema of the data returned by sql, which the data will be inserted into
    :type dest_table: str
    :param dest_fields: a list of str, naming the fields that the result will be inserted into.
    :type dest_fields: list
    :param batch_size: the number of insert values to batch together to speed up inserts. Default: 1000
    :type batch_size: int

    """

    template_fields = ('sql', 'dest_schema', 'dest_table', 'cleanup_query')
    template_ext = ('.sql', )

    @apply_defaults
    def __init__(self,
                 sql=None,
                 src_conn_id: str = None,
                 src_hook_config: dict = None,
                 dest_conn_id: str = None,
                 dest_hook_config: dict = None,
                 dest_schema: str = 'public',
                 dest_table: str = None,
                 dest_fields: list = None,
                 cleanup_query: str = None,
                 batch_size: int = 1000,
                 *args,
                 **kwargs):
        super(SQLToSQLOperator, self).__init__(*args, **kwargs)
        self.sql = sql
        self.src_conn_id = src_conn_id
        self.src_hook_config = src_hook_config
        self.cleanup_query = cleanup_query
        self.dest_conn_id = dest_conn_id
        self.dest_hook_config = dest_hook_config
        self.dest_schema = dest_schema
        self.dest_table = dest_table
        self.dest_fields = dest_fields
        self.batch_size = batch_size
        self.src_hook = None
        self.dest_hook = None


    def _get_hook(self, connection_id: str, hook_config: dict = None):
        """
        Retrieve the DbAPIHook for the supplied connection_id
        :param connection_id: a string naming the connection id to retrieve
        :param hook_config: a dict of properties that will be applied to the hook
        :return: the DbAPIHook
        """
        conn = BaseHook.get_connection(connection_id)

        allowed_conn_type = {'google_cloud_platform', 'jdbc', 'mssql',
                             'mysql', 'oracle', 'postgres',
                             'sqlite', 'vertica'}
        if conn.conn_type not in allowed_conn_type:
            raise AirflowException("The {} connection type is not supported by SQLToSQLOperator. " +
                                   "Supported connection types: {}".format(connection_id, list(allowed_conn_type)))
        
        if conn.conn_type == 'google_cloud_platform':
            hook = BigQueryHook(gcp_conn_id=connection_id)
        else:
            hook = conn.get_hook()
    
        if hook_config:
            self.log.info('Applying hook properties...')
            for key in hook_config.keys():
                setattr(hook, key, hook_config[key])

            self.log.info('Completed application of hook properties')

        return hook


    def _fetch_from_sql(self):
        """
        Load the source data from the source DbApiHook using the configured SQL
        :return: The result of DbApiHook.get_records
        """
        return self.src_hook.get_records(sql=self.sql)


    def execute(self, context):
        self.log.info('Retrieving the source hook: {}'.format(self.src_conn_id))
        self.src_hook = self._get_hook(connection_id=self.src_conn_id, hook_config=self.src_hook_config)
        self.log.info('Completed retrieval of the source hook')

        self.log.info('Retrieving the destination hook: {}'.format(self.dest_conn_id))
        self.dest_hook = self._get_hook(connection_id=self.dest_conn_id, hook_config=self.dest_hook_config)
        self.log.info('Completed retrieval of the destination hook')

        self.log.info('Reading SQL data: {}'.format(self.sql))
        result = self._fetch_from_sql()
        self.log.info('Completed loading {} records from SQL'.format(len(result)))

        if self.cleanup_query:
            self.log.info('Executing cleanup query: {}'.format(self.cleanup_query))
            self.dest_hook.run(sql=self.cleanup_query)
            self.log.info('Completed execution of cleanup query')

        self.log.info('Inserting retrieved records into destination')        
        self.dest_hook.insert_rows(table='{}.{}'.format(self.dest_schema, self.dest_table),
                                   rows=result,
                                   target_fields=self.dest_fields,
                                   commit_every=self.batch_size
                                    )
        self.log.info('Completed inserting records into destination')

