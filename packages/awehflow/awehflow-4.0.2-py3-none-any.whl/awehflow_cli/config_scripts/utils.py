import click
import re


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        click.echo(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        click.echo(f"An error occurred while reading the file '{file_path}': {e}")
        return None


def table_extraction_regex(sql_content):

    table_part_regex_str = (
        r"(" 
            # Checks for table_{{ data_interval_start.format("YYYYMMDD") }}
            r"([a-zA-Z0-9_.-]+?)_{{ data_interval_start\.format\([\'\"]YYYYMMDD[\'\"]\) }}"
            # Checks for table_{{ data_interval_end.format("YYYYMMDD") }}
            r"|([a-zA-Z0-9_.-]+?)_{{ data_interval_end\.format\([\'\"]YYYYMMDD[\'\"]\) }}"
            # Checks for generic table name
            r"|({{.*?}})"
            # Checks for literal table name e.g. my_table, sales_2023 (keep at end of checks)
            r"|([a-zA-Z0-9_.-]+)"
        r")"
    )

    table_pattern = re.compile(
        r"(?:FROM|JOIN)\s+\`"
        r"((?:{{.*?}}|[a-zA-Z0-9_.-]+))"  # project_id check
        r"\."
        r"((?:{{.*?}}|[a-zA-Z0-9_.-]+))"  # datase_id check
        r"\."
        + table_part_regex_str +
        r"\`",
        re.IGNORECASE
    )

    return table_pattern.findall(sql_content)


def write_output(file_path, index):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(index)
        click.echo(f"Successfully wrote content to '{file_path}'")
        return True
    except Exception as e:
        click.echo(f"Error: Could not write to file '{file_path}': {e}")
        return False