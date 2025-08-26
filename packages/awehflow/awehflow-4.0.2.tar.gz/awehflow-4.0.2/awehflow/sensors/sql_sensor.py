from time import sleep
from datetime import timedelta
import re

from airflow.version import version as airflow_version
from airflow.utils import timezone
from airflow.models.taskreschedule import TaskReschedule
from airflow.exceptions import AirflowSensorTimeout, AirflowSkipException, AirflowRescheduleException

if int(re.sub('[^0-9]', '', airflow_version)) < 240:
    from airflow.sensors.sql import SqlSensor
else:
    from airflow.providers.common.sql.sensors.sql import SqlSensor

class SqlSensor(SqlSensor):
    """
    Override of the default SqlSensor with modified 'execute' logic.  Sensor now fails quitely in soft_fail mode
    """
    def execute(self, context):
        started_at = timezone.utcnow()
        if self.reschedule:
            task_reschedules = TaskReschedule.find_for_task_instance(context['ti']) #pragma: no cover
            if task_reschedules:                                                    #pragma: no cover
                started_at = task_reschedules[0].start_date                         #pragma: no cover
        while not self.poke(context):
            if (timezone.utcnow() - started_at).total_seconds() > self.timeout:
                if self.soft_fail and not context['ti'].is_eligible_to_retry():
                    #self._do_skip_downstream_tasks(context)                        # Commented out this line so that skip logic is run as usual
                    self.log.warning("SENSOR TIMED OUT IN SOFT FAIL MODE")
                    raise AirflowSkipException('Snap. Time is OUT.')
                else:
                    raise AirflowSensorTimeout('Snap. Time is OUT.')
            if self.reschedule:                                                     #pragma: no cover
                reschedule_date = timezone.utcnow() + timedelta(                    #pragma: no cover
                    seconds=self.poke_interval)                                     #pragma: no cover
                raise AirflowRescheduleException(reschedule_date)                   #pragma: no cover
            else:
                sleep(self.poke_interval)
        self.log.info("Success criteria met. Exiting.")