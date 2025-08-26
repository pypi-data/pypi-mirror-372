import click
import os
import re
import yaml

from awehflow_cli.config_scripts.utils import read_file, table_extraction_regex


def extract_tables(sql: str) -> set:

    tables = []
    matches = table_extraction_regex(sql)
    for match_tuple in matches:
        project_id            = match_tuple[0]
        dataset_id            = match_tuple[1]
        table_id              = match_tuple[2]
        start_date_template   = match_tuple[3]
        end_date_template     = match_tuple[4]
        generic_template      = match_tuple[5]
        literal_template      = match_tuple[6]

        current_prefix = None
        is_literal = False
        is_generic = False

        if start_date_template:
            current_prefix = start_date_template
        elif end_date_template:
            current_prefix = end_date_template
        elif literal_template:
            is_literal = True
        elif generic_template:
            is_generic = True
            
        tables.append({
            "pdt": f"{project_id}.{dataset_id}.{table_id}",
            "name": table_id,
            "prefix": current_prefix,
            "is_literal": is_literal,
            "is_generic": is_generic
        })
    return tables


def extract_dependencies(index: str) -> set:
    dependencies = {
        "bq_sensor": set(),
        "sql_sensor": set()
    }
    try:
        data = yaml.safe_load(index)
        if not isinstance(data, dict):
            click.echo("Warning: Root of index content is not a dictionary.")
            return dependencies

        dependencies_list = data.get("dependencies", [])
        if not isinstance(dependencies_list, list):
            click.echo("Warning: 'dependencies' key is not a list or is missing.")
            return dependencies

        for dep_item in dependencies_list:
            if isinstance(dep_item, dict):
                operator = dep_item.get("operator", "")
                params = dep_item.get("params", {})

                if "BigQueryTableSensor" in operator:
                    project_id = params.get("project_id")
                    dataset_id = params.get("dataset_id")
                    table_id = params.get("table_id")
                    
                    if project_id and dataset_id and table_id:
                        pdt = f"{project_id}.{dataset_id}.{table_id}"
                        dependencies["bq_sensor"].add(pdt)
                    else:
                        click.echo(f"Warning: Incomplete dependency params in item: {dep_item}")
                elif "SqlSensor" in operator:
                    sql_query = params.get("sql")
                    if isinstance(sql_query, str):
                        # Regex to find "source = 'table_name'" or "source='table_name'"
                        source_matches = re.findall(
                            r"source\s*=\s*\'([a-zA-Z0-9_.-]+)\'",
                            sql_query,
                            re.IGNORECASE
                        )
                        for table_name in source_matches:
                            dependencies["sql_sensor"].add(table_name)

    except yaml.YAMLError as e:
        click.echo(f"Error parsing YAML string: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred during YAML processing: {e}")
    return dependencies


def validate_config(configs):
    try:
        config_paths = {}
        for root, dirs, files in os.walk(configs):
            if root == configs:
                for subdir_name in dirs:
                    usecase_path = os.path.join(root, subdir_name)
                    yml_file = None
                    sql_file = None

                    for item in os.listdir(usecase_path):
                        item_path = os.path.join(usecase_path, item)
                        if os.path.isfile(item_path):
                            if item.endswith('.yml'):
                                yml_file = item_path
                            elif item.endswith('.sql'):
                                sql_file = item_path

                    if yml_file and sql_file:
                        config_paths[subdir_name] = {
                            'yml_path': yml_file,
                            'sql_path': sql_file
                        }
                    elif yml_file or sql_file:
                        click.echo(f"Warning: In '{subdir_name}', either .yml or .sql file is missing. Found index: {bool(yml_file)}, SQL: {bool(sql_file)}")
                dirs[:] = []
            else:
                dirs[:] = []

    except Exception as e:
        click.echo(f"Error: Directory '{configs}' not found.")

    missing_dependencies_for_sql_tables = []

    for usecase, file_paths in config_paths.items():

        sql = read_file(file_paths['sql_path'])
        index = read_file(file_paths['yml_path'])

        tables = extract_tables(sql)
        dependencies = extract_dependencies(index)

        if not tables:
            click.echo("INFO: No tables were extracted from the SQL query. Nothing to validate.")
        else:
            for sql_table_info in tables:
                sql_pdt = sql_table_info["pdt"]
                matching = False
                
                if sql_pdt in dependencies["bq_sensor"]:
                    matching = True
                else:
                    base_name_to_check = None
                    if sql_table_info["prefix"]:
                        base_name_to_check = sql_table_info["prefix"]
                    elif sql_table_info["is_literal"]:
                        base_name_to_check = sql_table_info["name"]

                    if base_name_to_check in dependencies["sql_sensor"]:
                        matching = True
                if not matching:
                    missing_dependencies_for_sql_tables.append(sql_pdt)
        
    if matching:
        click.echo("✅ SUCCESS: All tables in the SQL query have corresponding dependency checks.")
    else:
        click.echo("❌ FAILURE: Some tables in the SQL query are missing dependency checks.")
        if missing_dependencies_for_sql_tables:
            click.echo("  The following tables lack dependency checks:")
            for missing_dep in missing_dependencies_for_sql_tables:
                click.echo(f"    - {missing_dep}")
