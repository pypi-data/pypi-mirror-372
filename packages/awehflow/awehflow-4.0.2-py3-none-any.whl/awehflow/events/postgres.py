import json
import logging

from airflow.providers.postgres.hooks.postgres import PostgresHook

from awehflow.events.base import EventHandler


class PostgresMetricsEventHandler(EventHandler):
    JOBS_SCHEMA = {
        'id': {
            'type': 'serial'
        },
        'run_id': {
            'type': 'varchar'
        },
        'dag_id': {
            'type': 'varchar'
        },
        'name': {
            'type': 'varchar'
        },
        'project': {
            'type': 'varchar'
        },
        'status': {
            'type': 'varchar'
        },
        'engineers': {
            'type': 'json'
        },
        'error': {
            'type': 'json'
        },
        'start_time': {
            'type': 'timestamp'
        },
        'end_time': {
            'type': 'timestamp'
        },
        'reference_time': {
            'type': 'timestamp'
        }
    }

    JOB_TASK_METRICS_SCHEMA = {
        'id': {
            'type': 'serial'
        },
        'run_id': {
            'type': 'varchar'
        },
        'dag_id': {
            'type': 'varchar'
        },
        'job_name': {
            'type': 'varchar'
        },
        'task_id': {
            'type': 'varchar'
        },
        'value': {
            'type': 'json'
        },
        'created_time': {
            'type': 'timestamp'
        },
        'reference_time': {
            'type': 'timestamp'
        }
    }

    def __init__(self, jobs_table, task_metrics_table, postgres_conn_id='postgres_jobs'):
        self.hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        self.jobs_table = jobs_table
        self.task_metrics_table = task_metrics_table

    def start(self, event):
        logging.info('start {}'.format(event))
        self.__upsert_job(event)

    def success(self, event):
        logging.info('success {}'.format(event))
        self.__upsert_job(event)

    def failure(self, event):
        logging.info('failure {}'.format(event))
        self.__upsert_job(event)

    def task_metric(self, event):
        logging.info('task_metric: {}'.format(event))
        self.__insert_task_metric(event)

    @staticmethod
    def __get_value(schema, event_body, key):
        if key not in schema:
            return event_body.get(key, '')
        if schema[key]['type'] == 'json':
            return json.dumps(event_body.get(key, ''))
        if schema[key]['type'] == 'timestamp':
            return str(event_body.get(key, ''))
        return event_body.get(key, schema[key].get('default_value', ''))

    def __upsert_job(self, event):
        body = event.get('body', {})
        columns = body.keys()
        values = [self.__get_value(self.JOBS_SCHEMA, body, column) for column in columns]
        value_placeholders = ['%s' for _ in values]
        update_columns = [column for column in columns if column not in ['run_id', 'dag_id']]
        update_values = ['EXCLUDED.{}'.format(column) for column in update_columns]
        sql = """
            INSERT INTO {table_name} ({columns})
            VALUES ({value_placeholders})
            ON CONFLICT ON CONSTRAINT run_id_dag_id_unique DO UPDATE SET ({update_columns}) = ({update_values})
        """.format(
            table_name=self.jobs_table,
            columns=','.join(columns),
            value_placeholders=','.join(value_placeholders),
            update_columns=','.join(update_columns),
            update_values=','.join(update_values)
        )

        self.hook.run(
            sql=sql,
            parameters=tuple(values)
        )

    def __insert_task_metric(self, event):
        body = event.get('body', {})
        columns = [key for key in self.JOB_TASK_METRICS_SCHEMA.keys() if key != 'id']
        values = [self.__get_value(self.JOB_TASK_METRICS_SCHEMA, body, column) for column in columns]
        value_placeholders = ['%s' for _ in values]
        sql = """
            INSERT INTO {table_name} ({columns})
            VALUES ({value_placeholders})
        """.format(
            table_name=self.task_metrics_table,
            columns=','.join(columns),
            value_placeholders=','.join(value_placeholders)
        )

        self.hook.run(
            sql=sql,
            parameters=tuple(values)
        )