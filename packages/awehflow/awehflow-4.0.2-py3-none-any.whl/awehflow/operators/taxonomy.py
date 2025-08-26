from typing import Optional
import re

from airflow.utils.decorators import apply_defaults
from airflow.operators.python import PythonVirtualenvOperator
from airflow.version import version as airflow_version

def set_policy_tag(project_id, dataset_id, table_names, policy_tags, gcp_conn_id, testing=False):
    from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery
    from google.cloud.bigquery import schema
    import logging

    # Internal methods
    def _get_table(project_id: str, dataset_id: str, table_name: str, client: bigquery.Client) -> bigquery.Table: 
        """Retrieve the table and schema using BQ Client

        Args:
            project_id (str): The project ID the table belongs to
            dataset_id (str): The dataset ID the table belongs to
            table_name (str): The name of the table
            client (bigquery.Client): The BigQuery client to use to retrieve info

        Returns:
            bigquery.Table: The BigQuery table object
        """
        # Construct table ID
        table_id = f'{project_id}.{dataset_id}.{table_name}'

        # Load table information including schema data
        try:
            table = client.get_table(table_id)
            return table
        except NotFound as e:
            logging.error(f'Table not found: {table_id}')
            return None

    def _column_is_pii(column, policy_tags):
        column_names = [col.lower() for policy_tag in policy_tags for col in policy_tags[policy_tag]['column_names']]
        return str(column.name).lower() in column_names
    
    def get_pii_tag(column, policy_tags):
        for policy_tag in policy_tags:
            if str(column.name).lower() in policy_tags[policy_tag]['column_names']:
                return policy_tags[policy_tag]['tag']
        raise TaxonomyException(f'{column} was not found in the policy tags.')
    
    def get_pii_description(column, policy_tags):
        for policy_tag in policy_tags:
            if str(column.name).lower() in policy_tags[policy_tag]['column_names']:
                return policy_tag
        raise TaxonomyException(f'{column} was not found in the policy tags.')
        
    def _schema_builder(original_schema:list , policy_tags: dict) -> list:
        """Builds a new schema set using the supplied schema list, and adding the policy tag to the supplied list of columns

        Args:
            original_schema (list): The original list of fields making up the schema
            column_names (list): The list of columns that the policy tag should be assigned to
            policy_tag (str): [description]

        Returns:
            list(bigquery.schema.SchemaField): The list of fields making up the schema
        """
        column_names = [col.lower() for policy_tag in policy_tags for col in policy_tags[policy_tag]['column_names']]

        logging.info(f'Processing columns: {column_names}')
        
        # Init an empty list object to store new schema
        new_schema = []
        
        for column in original_schema:
            if _column_is_pii(column, policy_tags):
                logging.info('Adding {} Policy Tag to column: {}'.format(get_pii_description(column, policy_tags), column.name))
                new_schema.append(bigquery.SchemaField(name=column.name,
                                                    field_type=column.field_type,
                                                    mode=column.mode,
                                                    description=column.description,
                                                    fields=column.fields,
                                                    policy_tags=schema.PolicyTagList((get_pii_tag(column, policy_tags),))))
            else:
                logging.debug(f'Not modifying column: {column.name}')
                new_schema.append(column)

        return new_schema

    def update_policy_tag(project_id: str, dataset_id: str, table_names: list, policy_tags: dict, gcp_conn_id: str): #pragma: no cover
        hook = BigQueryHook(
            gcp_conn_id=gcp_conn_id,
            use_legacy_sql=False
        )
        credentials = hook.get_credentials()
        credential_email = credentials.service_account_email
        logging.info(f"Created BigQueryHook with account: {credential_email}")

        client = hook.get_client()

        if isinstance(table_names, str):
            table_names = [table_names]

        if not isinstance(table_names, list):
            raise ValueError(f'table_names should be of type str or list, not of type {type(table_names)}')

        for table_name in table_names:
            logging.warning(f'Updating policy tags for [{project_id}.{dataset_id}.{table_name}]')
            # Get original schema
            table = _get_table(project_id=project_id, dataset_id=dataset_id, table_name=table_name, client=client)

            if not table:
                logging.warning(f'Table [{table_name}] not found in [{project_id}.{dataset_id}]')
                continue

            original_schema = table.schema
            table.schema = _schema_builder(original_schema, policy_tags=policy_tags)
            client.update_table(table, ["schema"])

    if testing: #pragma: no cover
        return {
            '_get_table': _get_table,
            '_column_is_pii': _column_is_pii,
            'get_pii_tag': get_pii_tag,
            'get_pii_description': get_pii_description,
            '_schema_builder': _schema_builder,
            'update_policy_tag': update_policy_tag
            
        }

    update_policy_tag(project_id, dataset_id, table_names, policy_tags, gcp_conn_id) #pragma: no cover
    
class ApplyTaxonomyOperator(PythonVirtualenvOperator): #pragma: no cover
    # """
    # Adds policy tags to columns in a BigQuery Table.

    # param project_id: The name of the project that the BigQuery table is in.
    # type project_id: str
    # param dataset_id_id: The name of the dataset that the BigQuery table is in.
    # type project_id: str
    # param table_name: The table name that the policy tags should be applied to.
    # type table_name: str
    # param policy_tags: The policy tags that needs to be applied to the table.
    # type policy_tags: dict
    
    # """
    @apply_defaults
    def __init__(
            self, 
            task_id: str, 
            project_id: str, 
            dataset_id: str, 
            table_names: list, 
            policy_tags: dict,
            gcp_conn_id: str='gcp_default',
            bigquery_conn_id: Optional[str] = None,
            *args, **kwargs):
        
        if bigquery_conn_id:
            gcp_conn_id = bigquery_conn_id

        requirements=["google-cloud-bigquery==2.13.1"]
        if int(re.sub('[^0-9]', '', airflow_version)) >= 240:
            requirements=["google-cloud-bigquery==3.11.0"]

        super(ApplyTaxonomyOperator, self).__init__(
            task_id=task_id,
            python_callable=set_policy_tag,
            requirements=requirements,
            system_site_packages=True,
            op_kwargs={
                'project_id': project_id,
                'dataset_id': dataset_id,
                'table_names': table_names,
                'policy_tags': policy_tags,
                'gcp_conn_id': gcp_conn_id,
            },
            *args, **kwargs
        )

class TaxonomyException(Exception):
    pass