from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.models.variable import Variable
import urllib.request
import hashlib
import ssl

class HttpChangeSensor(BaseSensorOperator):
    """
    The HttpChangeSensor can be used to detect a change in a URL
    If the content of the URL changes between various runs of the Sensor the result is True
    If the content remains un-changed the result is False

    The content of the page is read and MD5 hashed, the hash is stored in Airflow variables to remain available between
    runs.
    """

    template_fields = ('url', 'start_tag', 'end_tag')

    @apply_defaults
    def __init__(self,
                 url: str,
                 start_tag: str = None,
                 end_tag: str = None,
                 *args, **kwargs):
        """
        Instantiate an instance of HttpChangeSensor
        :param url: The URL to monitor
        :param start_tag: A string in the URL content from which change detection will start.
            Can be left blank to scan entire URL content
        :param end_tag: A string in the URL content at which change detection should stop.
            Can be left blank
        :param args:
        :param kwargs:
        """
        super(HttpChangeSensor, self).__init__(*args, **kwargs)
        self.url = url
        self.start_tag = start_tag.lower().encode('utf-8') if start_tag else None
        self.end_tag = end_tag.lower().encode('utf-8') if end_tag else None
        self.url_hash = '{}_{}_{}'.format(self.dag_id, self.task_id, hashlib.md5(url.lower().encode('utf-8')).hexdigest())

    def poke(self, context):
        """
        Override of the BaseSensor poke command
        :param context: The execution context
        :return: True if the page changed, False if not
        """
        self.log.info(f"Checking url {self.url} to see if data has changed")

        check_result = False

        self.log.info("Loading previous page content hash")
        last_hash = Variable.get(self.url_hash, default_var=None)

        self.log.info("Retrieving page content")
        context = ssl._create_unverified_context()

        page_object = urllib.request.urlopen(self.url, context=context)
        page_content = str(page_object.read()).lower().encode('utf-8')

        self.log.info("Loaded {} bytes of page content".format(len(page_content)))

        start_idx = 0
        end_idx = len(page_content)

        if self.start_tag:
            self.log.info("Start tag specified, scanning...")
            start_idx = page_content.find(self.start_tag)
            if start_idx != -1:
                self.log.info("Located start tag at index: {}".format(start_idx))
                start_idx = start_idx + len(self.start_tag)
                self.log.info('Start_idx calculated as {}'.format(start_idx))

        if self.end_tag:
            self.log.info("End tag specified, scanning...")
            end_idx = page_content.find(self.end_tag)
            if end_idx != -1:
                end_idx = end_idx - 1
            else:
                end_idx = len(page_content)

            self.log.info("Located end tag at index: {}".format(end_idx))

        page_section = page_content[start_idx:end_idx+1]
        self.log.info("Calculating MD5 hash for {} bytes of page section".format(len(page_section)))
        section_hash = hashlib.md5(page_section).hexdigest()

        self.log.info("Section MD5 hash calculated as {}".format(section_hash))

        if last_hash:
            if last_hash != section_hash:
                check_result = True
        else:
            self.log.warning("Last hash instance does not exist")

        self.log.info("Saving current section hash as last hash variable")
        Variable.set(key=self.url_hash, value=section_hash)

        return check_result
