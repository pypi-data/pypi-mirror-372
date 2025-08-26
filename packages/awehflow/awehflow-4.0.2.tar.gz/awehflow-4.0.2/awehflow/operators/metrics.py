from airflow.models.baseoperator import BaseOperator

from typing import Any

class MetricOperator(BaseOperator):
    """Execute metric queries against conn_id and emit data to a metrics table

    Args:
        BaseOperator (_type_): _description_
    """

    def __init__(self, 
            metric_key: str,
            sql: str,
            platform: str,
            source: str,
            reference_date: str,
            src_conn_id: str='metric_source',
            src_hook_config: dict={},
            dest_conn_id='metric_destination',
            dest_hook_config: dict={},
            *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context: Any):
        self.log.info('Metrics will be added here')
        return super().execute(context)

