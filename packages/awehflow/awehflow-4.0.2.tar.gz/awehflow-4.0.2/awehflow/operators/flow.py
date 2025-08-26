import logging
import re

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.version import version as airflow_version

from awehflow.utils import utc_now, JobStatus


class EventEmittingOperator(BaseOperator):
    @apply_defaults
    def __init__(
            self,
            event_handlers=None,
            *args, **kwargs):
        """
        :param event_handlers: List of event handlers to emit events to
        """

        super(EventEmittingOperator, self).__init__(*args, **kwargs)
        if event_handlers is None:
            event_handlers = []
        self.event_handlers = event_handlers

    def execute(self, context):
        raise Exception("EventEmittingOperator should be extended")

    def emit_event(self, event_name, body={}):
        for handler in self.event_handlers:
            try:
                handler.handle({
                    'name': event_name,
                    'body': body
                })
            except Exception as e:
                logging.error('Error handling event: {}'.format(e))


class FlowOperator(EventEmittingOperator):
    @apply_defaults
    def __init__(
            self,
            project,
            job_name,
            engineers,
            *args, **kwargs):
        """
        :param job_name: Name of the pipeline job. Typically just use the dag_name
        :param engineers: list of engineers responsible for the pipeline
        """
        super(FlowOperator, self).__init__(*args, **kwargs)
        self.project = project
        self.job_name = job_name
        self.engineers = engineers


class StartOperator(FlowOperator):
    def execute(self, context):
        if int(re.sub('[^0-9]', '', airflow_version)) < 220:
            next_execution_date = context['next_execution_date']
        else:
            next_execution_date = context['data_interval_end']

        self.emit_event('start', {
            'run_id': context['dag_run'].run_id,
            'dag_id': self.dag.dag_id,
            'name': self.job_name,
            'project': self.project,
            'engineers': self.engineers,
            'status': JobStatus.RUNNING,
            'start_time': utc_now(),
            'reference_time': next_execution_date
        })


class SuccessOperator(FlowOperator):
    def execute(self, context):
        self.emit_event('success', {
            'run_id': context['dag_run'].run_id,
            'dag_id': self.dag.dag_id,
            'name': self.job_name,
            'project': self.project,
            'engineers': self.engineers,
            'status': JobStatus.SUCCESS,
            'end_time': utc_now()
        })


class FailureOperator(FlowOperator):
    def execute(self, context):
        self.emit_event('failure', {
            'run_id': context['dag_run'].run_id,
            'dag_id': self.dag.dag_id,
            'name': self.job_name,
            'project': self.project,
            'engineers': self.engineers,
            'status': JobStatus.FAILURE,
            'error': {
                'task_id': context['task_instance'].task_id,
                'message': str(context.get('exception', '')),
                'log_url': context['task_instance'].log_url
            },
            'end_time': utc_now()
        })