import click
import logging
import os

from awehflow_cli.config_scripts.generate_configs import generate_config
from awehflow_cli.config_scripts.validate_configs import validate_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


@click.group(help="CLI tool for awehflow")
def aweh():
    """ main command """
    pass

@aweh.command()
@click.option("-sql_file", type=str, required=True, help="The sql file")
@click.pass_context
def gencon(ctx, sql_file):
    """Generates index.yml config from a provided .sql file"""
    from pathlib import Path
    current_dir = Path(os.getcwd())
    sql_files_list = list(current_dir.glob('*.sql'))
    if len(sql_files_list)==0:
        click.echo("Please navigate to directory that contains the sql file")
        ctx.exit(1)
    else:
        usecase = click.prompt("What is the usecase? e.g. client_transactions", type=str)
        start_date = click.prompt("What is the start date? e.g. 2025-01-01", type=str)

        schedule = click.prompt(
            "Choose a schedule for the DAG e.g. 0 * * * * (hourly), 0 3 * * * (daily @ 03:00), 0 3 1 * * (monthly on the 1st @ 03:00)",
            type=str
        )

        source_project = click.prompt("Enter the source project", type=str)
        source_dataset = click.prompt("Enter the source dataset", type=str)

        target_project = click.prompt("Enter the target project", type=str)
        target_dataset = click.prompt("Enter the target dataset", type=str)

        partition = click.prompt("Would you like to partition your table?", type=click.Choice(['Y', 'n']), default='Y', show_default=True)

        if partition =="Y":
            partition = {
                "partition_field": click.prompt("What field would you like to partition on?", type=str),
                "partition_type": click.prompt("How would you like to partition?", type=click.Choice(['HOUR', 'DAY', 'MONTH', 'YEAR']))
            }
        else:
            partition = None

        cluster = click.prompt("Would you like to add clustering to your table?", type=click.Choice(['Y', 'n']), default='Y', show_default=True)

        if cluster =="Y":
            cluster_fields = click.prompt(
                "What fields would you like to cluster on? e.g. id, date. NB: BigQuery allows maximum 4 clustering fields.",
                type=str
            )
        else:
            cluster_fields = None

        generate_config(sql_file, usecase, start_date, schedule, source_project, source_dataset, target_project, target_dataset, partition, cluster_fields)


@aweh.command()
@click.option("-path_to_configs_dir", type=str, required=True, help="Specify the path to the configs directory e.g. dags/prepared/configs")
def validate(path_to_configs_dir):
    """Validates all the index.yml configs against their respective .sql files"""
    validate_config(path_to_configs_dir)


if __name__ == '__main__':
    aweh()