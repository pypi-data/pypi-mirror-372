import click
import re

from awehflow_cli.config_scripts.utils import read_file, table_extraction_regex, write_output


def generate_dependency_checks(sql):

    matches = table_extraction_regex(sql)

    if not matches:
        return ""

    dependencies_string = "dependencies:"
    unique_tables = set()

    for match_tuple in matches:
        project_id            = match_tuple[0]
        dataset_id            = match_tuple[1]
        table_id              = match_tuple[2]
        start_date_template   = match_tuple[3]
        end_date_template     = match_tuple[4]
        generic_template      = match_tuple[5]
        literal_template      = match_tuple[6]

        date_template_table = None

        if start_date_template:
            date_template_table = start_date_template
            param_table_id_for_yaml = f'{date_template_table}_{{{{ data_interval_start.format("YYYYMMDD") }}}}'
            # Retrieving table name for dependency id
            temp_id_suffix = re.sub(r'[^a-zA-Z0-9_]', '_', date_template_table)
            dependency_id_suffix = re.sub(r'_+', '_', temp_id_suffix).strip('_') or "date_templated_table"

        elif end_date_template:
            date_template_table = end_date_template
            param_table_id_for_yaml = f'{date_template_table}_{{{{ data_interval_end.format("YYYYMMDD") }}}}'
            # Retrieving table name for dependency id
            temp_id_suffix = re.sub(r'[^a-zA-Z0-9_]', '_', date_template_table)
            dependency_id_suffix = re.sub(r'_+', '_', temp_id_suffix).strip('_') or "date_templated_table"

        elif generic_template:
            param_table_id_for_yaml = generic_template
            # Retrieving table name for dependency id
            temp_id = generic_template.replace("{{", "").replace("}}", "")
            temp_id = temp_id.replace("params.", "").replace(".params", "")
            temp_id = temp_id.replace("var.value.", "").replace(".var.value", "")
            temp_id = temp_id.replace("data_interval_start.format", "dtstartfmt")
            temp_id = temp_id.replace("data_interval_end.format", "dtendfmt")
            temp_id = temp_id.strip()
            temp_id = re.sub(r'[^a-zA-Z0-9_]+', '_', temp_id)
            temp_id = re.sub(r'_+', '_', temp_id).strip('_')
            dependency_id_suffix = temp_id if temp_id else "generic_templated_table"

        elif literal_template:
            param_table_id_for_yaml = literal_template
            # Retrieving table name for dependency id
            temp_id_suffix = re.sub(r'[^a-zA-Z0-9_]', '_', literal_template)
            dependency_id_suffix = re.sub(r'_+', '_', temp_id_suffix).strip('_') or "literal_table"

        else:
            click.echo(f"Warning: Could not categorize table string: '{table_id}' from tuple: {match_tuple}")
            param_table_id_for_yaml = table_id
            dependency_id_suffix = "unknown_table_type"

        # Ensuring distinct dependency checks are created
        table_identifier_for_uniqueness = f"{project_id}.{dataset_id}.{table_id}"

        if table_identifier_for_uniqueness not in unique_tables:
            unique_tables.add(table_identifier_for_uniqueness)

            dependencies_string += f"""
  - id: 'dependency_{dependency_id_suffix}'
    operator: 'airflow.contrib.sensors.bigquery_sensor.BigQueryTableSensor'
    params:
      project_id: '{project_id}'
      dataset_id: '{dataset_id}'
      table_id: '{param_table_id_for_yaml}'
    poke_interval: 60
    timeout: 10800
    mode: 'reschedule'"""

    return dependencies_string


def generate_partitioning(partition):
      if not partition:
          return ""
      else:
          partitioning = f"""
      time_partitioning:
        type: '{partition["partition_type"]}'
        field: '{partition["partition_field"]}'"""
      
      return partitioning


def generate_cluster_fields(cluster_fields):
    if not cluster_fields:
      return ""

    items = cluster_fields.split(',')
    processed_items = [item.strip() for item in items if item.strip()]
    if len(processed_items) > 4:
        raise ValueError(f"{len(processed_items)} cluster fields provided which exceeds the maximum allowed of 4.")
    if not processed_items:
      return ""

    output_lines = ["cluster_fields:"]
    for item in processed_items:
      output_lines.append(f"        - '{item}'")
    
    return "\n".join(output_lines)


def generate_config(file, usecase, start_date, schedule, source_project, source_dataset, target_project, target_dataset, partition, cluster_fields):

    sql = read_file(file)
    dependencies = generate_dependency_checks(sql)
    partitioning = generate_partitioning(partition)
    clustering = generate_cluster_fields(cluster_fields)

    index = f"""name: '{usecase}'
start_date: '{start_date}'
catchup: false
schedule: '{schedule}'
version: 1
engineers:
  - name: ''
  - email: ''
alert_on:
  - 'failure'
params:
  default:
    source_project: '{source_project}'
    source_dataset: '{source_dataset}'
    source_dataset_latest: '{source_dataset}_latest'
    target_project: '{target_project}'
    target_dataset: '{target_dataset}'
    target_dataset_latest: '{target_dataset}_latest'
  staging:
    target_project: ''
  production:
    target_project: ''

default_dag_args:
  gcp_conn_id: ''
  write_disposition: 'WRITE_TRUNCATE'
  use_legacy_sql: false
  poke_interval: 1800

{dependencies}

tasks:
  - id: 'create_{usecase}'
    operator: 'awehflow.operators.gcp.BigQueryJobOperator'
    params:
      destination_dataset_table: '{'{{ params.target_project }}.{{ params.target_dataset }}'}.{usecase}_{'{{ data_interval_start.format("YYYYMMDD") }}'}'
      sql: 'configs/{usecase}/{usecase}.sql'
      {partitioning}
      {clustering}

  - id: 'get_latest_{usecase}'
    operator: 'awehflow.operators.gcp.BigQueryPushFirstResultToXComOperator'
    params:
      use_legacy_sql: false
      sql: SELECT MAX(suffix)
        FROM (
          SELECT SUBSTR(table_name, LENGTH('{usecase}_') + 1) as suffix
          FROM `{'{{ params.target_project }}.{{ params.target_dataset }}'}.INFORMATION_SCHEMA.TABLES`
          WHERE table_name LIKE '{usecase}_2%'
        )
    upstream: 
      - 'create_{usecase}'

  - id: 'create_{usecase}_latest'
    operator: 'awehflow.operators.gcp.BigQueryJobOperator'
    params:
      destination_dataset_table: '{'{{ params.target_project }}.{{ params.target_dataset_latest }}'}.{usecase}'
      sql: SELECT * FROM `{'{{ params.target_project }}.{{ params.target_dataset }}'}.{usecase}_'{{{{ ti.xcom_pull(task_ids="get_latest_{usecase}")[0] }}}}'`
    upstream: 
      - 'get_latest_{usecase}'

  - id: 'update_table_descriptions'
    operator: 'awehflow.operators.gcp.BigQueryUpdateTableDescriptionOperator'
    params:
      description_data: 'prepared/configs/{usecase}/field_descriptions.conf'
      destination_dataset_tables: 
        - '{'{{ params.target_project }}.{{ params.target_dataset_latest }}'}.{usecase}'
        - '{'{{ params.target_project }}.{{ params.target_dataset }}'}.{usecase}_{'{{ data_interval_end.format("YYYYMMDD") }}'}'
    upstream: 
      - 'create_{usecase}_latest'

  - id: 'save_bigquery_job_metrics'
    operator: 'awehflow.operators.gcp.BigQueryJobTaskMetricOperator'
    params:
      task_ids:
        - 'create_{usecase}'
        - 'create_{usecase}_latest'
    upstream:
      - 'update_table_descriptions'
"""

    write_output('index.yml', index)