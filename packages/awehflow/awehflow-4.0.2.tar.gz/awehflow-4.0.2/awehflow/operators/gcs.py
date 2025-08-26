from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.ssh.hooks.ssh import SSHHook
from pathlib import Path
from datetime import datetime as dt
from random import randint
import time
from typing import List
import fnmatch
import os


class BigQueryCSVExtractAndComposeOperator(BaseOperator):
    """
    Uses Google Cloud Storage compose to extract a BigQuery table to a single CSV single file
    """

    template_fields = (
        'source_project',
        'source_dataset',
        'source_table',
        'destination_object_name',
        'temp_bucket_name', 
        'temp_dataset_name', )

    @apply_defaults
    def __init__(self,
                 source_project: str,
                 source_dataset: str,
                 source_table: str,
                 destination_object_name: str,
                 temp_bucket_name: str,
                 temp_dataset_name: str,
                 print_header: bool = True,
                 field_delimiter: str = ',',
                 bigquery_conn_id: str = 'bigquery_default',
                 gcp_conn_id: str = 'gcp_conn_id',
                 location=None,
                 *args, **kwargs) -> None:

        """
        Create an instance of the BigQueryCSVExtractAndComposeOperator
        :param source_dataset_table: The source BigQuery table to extract, including the data set and table name ie. dev_temp.some_table_to_extract
        :param destination_object_name: The destination filename as a bucket URI ie gs://dev_extract_data/some_sub_folder/my_extract.csv
        :param temp_bucket_name: The temporary bucket area where files can be extracted and composed
        :param temp_dataset_name: A temp dataset where temporary tables can be created and saved, while processing (can also pass in project as <project>.<dataset>)
        :param print_header: Whether or not the extracted data should contain a header or not
        :param field_delimiter: What kind of field delimiter to use. Default: ,
        :param bigquery_conn_id: The name of the google_cloud_platform connection to use for queries.  The user should have R/W permission to the temp dataset
        :param gcp_conn_id: The name of the google_cloud_platform connection to use for GCS jobs.  The connection should have R/W permission to the destination bucket and temp bucket
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.source_project = source_project
        self.source_dataset = source_dataset
        self.source_table = source_table
        self.destination_object_name = destination_object_name
        self.temp_bucket_name = temp_bucket_name.strip('/')
        self.temp_dataset_name = temp_dataset_name
        self.print_header = print_header
        self.field_delimiter = field_delimiter
        self.bigquery_conn_id = bigquery_conn_id
        self.gcp_conn_id = gcp_conn_id
        self.location = location

        # place holders for execute method
        self.gcs_hook = None
        self.bq_hook = None

    def execute(self, context):
        """
        Execute the BigQueryCSVExtractAndComposeOperator to extract a biq query table to a bucket and then compose the parts into a single CSV file
        :param context: The airflow context to execute on
        :return:
        """

        if self.gcs_hook is None:
            self.log.info('Creating GCSHook')
            self.gcs_hook = GCSHook(gcp_conn_id=self.gcp_conn_id)
            credentials = self.gcs_hook.get_credentials()
            credential_email = credentials.service_account_email
            self.log.info(f"Created GCSHook with account: {credential_email}")

        if self.bq_hook is None:
            self.log.info('Creating BigQueryHook')
            self.bq_hook = BigQueryHook(gcp_conn_id=self.bigquery_conn_id, location=self.location)
            credentials = self.bq_hook.get_credentials()
            credential_email = credentials.service_account_email
            self.log.info(f"Created BigQueryHook with account: {credential_email}")

        compose_bucket_name, compose_filename = self.get_bucket_and_filename(object_name=self.destination_object_name)
        self.log.info('Calculated final compose_bucket_name [{}] and compose_filename [{}]'.format(compose_bucket_name, compose_filename))

        working_bucket_name, junk_data = self.get_bucket_and_filename(object_name=self.temp_bucket_name + '/junk.dat')
        self.log.info('Calculated working_bucket_name: {}'.format(working_bucket_name))

        tmp_file_uniq = 'data_extract_tmp_' + dt.now().strftime('%Y%m%H%M%S') + '_' + str(randint(1, 100))
        tmp_parts_name = tmp_file_uniq + '_*.csv'
        tmp_compose_file = 'composed_data_' + tmp_file_uniq + '.csv'

        try:
            if self.print_header:
                self.log.info('Header requested so generating header tbl and file')

                tmp_header_filename = self.temp_bucket_name + '/_header_' + tmp_file_uniq + '_*.csv'
                tmp_header_table_name = '{}.{}_header_data'.format(self.temp_dataset_name, tmp_file_uniq)
                tmp_split = tmp_header_table_name.replace(":", ".").split(".")
                if len(tmp_split) == 3:
                    project_id, dataset_id, table_id = tmp_split
                    self.log.info(f'Getting project_id from temp_dataset_name argument: {project_id}.{dataset_id}.{table_id}')

                else:
                    dataset_id, table_id = tmp_split
                    project_id = self.bq_hook.project_id
                    self.log.info(f'Getting project_id from bq_hook {project_id}.{dataset_id}.{table_id}')


                self.log.info('Defined tmp_header_filename [{}] and tmp_header_table_name [{}]'.format(tmp_header_filename, tmp_header_table_name))
                self.log.info('Creating empty header table [{}]'.format(tmp_header_table_name))

                header_table_created = False

                try:
                    header_job_id = self.bq_hook.insert_job(
                        configuration = {
                            "query": {
                                "query": f'SELECT * FROM `{self.source_project}.{self.source_dataset}.{self.source_table}` WHERE 1=0 LIMIT 1',
                                "useLegacySql": False,
                                "writeDisposition": "WRITE_TRUNCATE",
                                "destinationTable": {
                                    "projectId": project_id,
                                    "datasetId": dataset_id,
                                    "tableId": table_id
                                }
                            }
                        },
                        location=self.location
                    )

                    header_job = self.bq_hook.get_job(job_id=header_job_id)
                    while not header_job.done():
                        self.log.info(f'Waiting for header query [{header_job_id}]...')
                        time.sleep(1)

                    header_table_created = True

                    self.log.info('Exporting header table [{}] to file [{}]'.format(tmp_header_table_name, tmp_header_filename))
                    
                    extract_job_id = self.bq_hook.insert_job(
                        configuration={
                            "extract": {
                                "sourceTable": {
                                    "projectId": project_id,
                                    "datasetId": dataset_id,
                                    "tableId": table_id
                                },
                                "destinationUris": [f'gs://{working_bucket_name}/{tmp_header_filename}'],
                                "printHeader": True,
                                "fieldDelimiter": self.field_delimiter,
                                "destinationFormat": "CSV" 
                            }
                        }
                    )

                    extract_job = self.bq_hook.get_job(job_id=extract_job_id)
                    while not extract_job.done():
                        self.log.info(f'Waiting for extract job [{extract_job_id}]...')
                        time.sleep(1)

                    self.log.info('Completed export of header table data')
                finally:
                    if header_table_created:
                        try:
                            self.bq_hook.delete_table(table_id=f'{self.source_project}.{tmp_header_table_name}', not_found_ok=True)
                        except ValueError:
                            self.bq_hook.delete_table(table_id=tmp_header_table_name, not_found_ok=True) 

            self.log.info("Extracting table data to tmp_parts_name [{}]".format(tmp_parts_name))
            final_extract_job_id = self.bq_hook.insert_job(
                configuration = {
                    "extract": {
                        "sourceTable": {
                                "projectId": self.source_project,
                                "datasetId": self.source_dataset,
                                "tableId": self.source_table,
                            },
                        "destinationUris": [f'gs://{working_bucket_name}/{tmp_parts_name}'],
                        "printHeader": False,
                        "fieldDelimiter": self.field_delimiter,
                        "destinationFormat": "CSV" 
                    }
                }
            )

            final_extract_job = self.bq_hook.get_job(job_id=final_extract_job_id)
            while not final_extract_job.done():
                self.log.info(f'Waiting for final extract job [{final_extract_job_id}]...')
                time.sleep(1)

            self.log.info('Completed extraction of primary table')
            self.log.info('Listing file parts matching [{}] to compose'.format(tmp_file_uniq))

            source_list = self.list_extract_files(working_bucket_name, tmp_file_uniq)
            self.log.info('Composing tmp_compose_file from source_list')
            self.log.info('source_list: {}'.format(source_list))
            self.log.info('-->')
            self.log.info('tmp_compose_file: {}'.format(tmp_compose_file))

            self.gcs_hook.compose(working_bucket_name,
                         source_objects=source_list,
                         destination_object=tmp_compose_file
                )

            self.log.info('Copying tmp_compose_file [{}/{}] to final compose_filename [{}/{}]'.format(
                self.temp_bucket_name,
                tmp_compose_file,
                compose_bucket_name,
                compose_filename
            ))

            self.gcs_hook.copy(source_bucket=working_bucket_name, source_object=tmp_compose_file,
                               destination_bucket=compose_bucket_name,
                               destination_object=compose_filename)

            self.log.info('Completed header-less extract & compose')
        finally:
            self.log.info('Deleting temp files created in [{}] during export process'.format(working_bucket_name))
            source_list = self.list_extract_files(bucket_name=working_bucket_name, file_pattern=tmp_file_uniq)
            for src in source_list:
                self.log.info('Deleting file [{}]'.format(src))
                self.gcs_hook.delete(working_bucket_name, src) # pragma: no cover

    def get_bucket_and_filename(self, object_name):
        """
        Split the gs:// URI for the destination object to a bucket_name and file_name
        :param object_name: The cloud storage URI
        :return: a tuple containing two variables, the bucket_name and the file_name component
        """
        bucket_path = Path(object_name.replace('gs:/', ''))
        bucket_name = str(bucket_path.parent).split('/')[1]
        dest_filename = object_name.replace('gs://' + bucket_name + '/', '')
        return bucket_name, dest_filename

    def list_extract_files(self, bucket_name, file_pattern):
        source_list = []

        file_list = self.gcs_hook.list(bucket_name)
        for filename in file_list:

            if file_pattern in str(filename):
                self.log.info('Found tmp file [{}], adding to source list'.format(filename))

                if 'header' in str(filename):
                    source_list.insert(0,filename)
                else:
                    source_list.append(filename)

        return source_list

class RecursiveComposeGCSFilesOperator(BaseOperator):
    """
    Recursively composes files from a Google Cloud Storage bucket until there's only one file left.
    Allows to compose more than 32 files, which is the GCS limit

    :param gcp_conn_id: The connection ID to use when connecting to Google Cloud Platform.
    :type gcp_conn_id: str
    :param bucket_name: The name of the Google Cloud Storage bucket.
    :type bucket_name: str
    :param source_prefix: The prefix for the source objects in the bucket. F.e 'transactions_2024'
    :type source_prefix: str
    :param destination_blob: The name of the composed destination blob INCLUDING FILE TYPE. F.e 'transactions.csv'
    :type destination_blob: str
    """
    
    template_fields = ['bucket_name', 'source_prefix', 'destination_blob'] # Allows airflow variable replacement
    
    def __init__(
            self, 
            gcp_conn_id: str = None, 
            bucket_name: str = None,
            source_prefix: str = None,
            destination_blob: str = None,
            *args, **kwargs
        ):
        super(RecursiveComposeGCSFilesOperator, self).__init__(*args, **kwargs)
        self.gcp_conn_id = gcp_conn_id
        self.bucket_name = bucket_name
        self.source_prefix = source_prefix
        self.destination_blob = destination_blob

    def rename_blob(self, blob_name):
        # Copy the source blob to the destination
        self.gcs_hook.copy(source_bucket=self.bucket_name, source_object=blob_name, destination_object=self.destination_blob)

        # Delete the original blob
        self.gcs_hook.delete(bucket_name=self.bucket_name, object_name=blob_name)
        self.log.info(f'Blob {blob_name} renamed to {self.destination_blob}')


    def compose_files(self, files: List[str]):
        """
        Recursively composes files from the given list until there's only one file left.

        :param files: List of file names to compose.
        :type files: List[str]
        """
        self.log.info("Composing files: %s", files)

        files_to_compose = files[:32]  # Google Cloud Storage has a limit of 32 files per compose operation

        # {self.source_prefix} in destination_object ensures that the dest blob adheres to source_prefix for recursive compose
        # _{len(files)}' ensures unique name and doesn't try to overwrite another object
        # {self.destination_blob.rsplit('.')[-1]} maintains destination object type
        self.gcs_hook.compose(bucket_name=self.bucket_name, source_objects=files_to_compose, destination_object=f'{self.source_prefix}_{len(files)}.{self.destination_blob.rsplit(".")[-1]}')
        self.log.info("Composed files into: %s", f'{self.source_prefix}_{len(files)}.{self.destination_blob.rsplit(".")[-1]}')
        
        # Remove the files that were composed
        for file_name in files_to_compose:
            self.log.info("Deleting file: %s", file_name)
            self.gcs_hook.delete(bucket_name=self.bucket_name, object_name=file_name)

        # Recursively call compose_files with remaining files - includes previously composed blob(s)
        remaining_blobs = list(self.gcs_hook.get_conn().bucket(self.bucket_name).list_blobs(prefix=self.source_prefix))
        remaining_files = [blob.name for blob in remaining_blobs]

        if len(remaining_files) == 1:
            self.log.info("Only one file left. Compose operation completed.")
            return remaining_files
        
        return self.compose_files(remaining_files)

    def execute(self, context):
        self.gcs_hook = GCSHook(gcp_conn_id=self.gcp_conn_id)
        blobs = list(self.gcs_hook.get_conn().bucket(self.bucket_name).list_blobs(prefix=self.source_prefix))

        if len(blobs) == 1:
            self.log.info("1 file found. No need to compose.")
            self.log.info(blobs[0].name)
            self.rename_blob(blobs[0].name)
        elif len(blobs) == 0:
            self.log.info("0 files found. Nothing to compose.")
        else:
            files = [blob.name for blob in blobs]
            composed_blob = self.compose_files(files)
            self.log.info(composed_blob[0])
            self.rename_blob(composed_blob[0])

class SftpToGcsOperator(BaseOperator):
    template_fields = ['source_folder', 'file_string', 'gcs_bucket_name']
    """
    A custom Airflow operator that extracts csv files from an sftp server and drops it on a GCS bucket. 

    :param gcp_conn_id: The connection ID to use when connecting to Google Cloud Platform.
    :type gcp_conn_id: str
    :param sftp_conn_id: The connection ID to use when connecting to the SFTP server.
    :type sftp_conn_id: str
    :param source_folder: The source folder on sftp server where the files are located (None if in user home directory).
    :type source_folder: str
    :param file_string: The file string to look and match target file(s) with (use * for wildcard)
    :type file_string: str
    :param gcs_bucket_name: The name of the gcs bucket to move the file(s) to
    :type gcs_bucket_name: str
    :param dest_folder: The destination folder to write file(s) to in gcs bucket
    :type dest_folder: str
    :param move_object: Set to True to delete source file(s)
    :type move_object: bool
    :param fail_on_missing_file: Set to True to fail when no file(s) are matched on sftp server
    :type move_object: bool
    """

    @apply_defaults
    def __init__(
        self,
        gcp_conn_id: str = None,
        sftp_conn_id: str = None,
        source_folder: str = '',
        file_string: str = None,
        gcs_bucket_name: str = None,
        dest_folder: str = '',
        move_object: bool = False,
        fail_on_missing_file: bool = False,
        *args, **kwargs
    ):
        super(SftpToGcsOperator, self).__init__(*args, **kwargs)
        self.gcp_conn_id = gcp_conn_id
        self.sftp_conn_id = sftp_conn_id
        self.source_folder = source_folder
        self.file_string = file_string
        self.gcs_bucket_name = gcs_bucket_name
        self.dest_folder = dest_folder
        self.move_object = move_object
        self.fail_on_missing_file = fail_on_missing_file

    def _get_file(self, sftp):
        files_on_server = sftp.listdir(self.source_folder)
        matching_files = [file for file in files_on_server if fnmatch.fnmatch(file, self.file_string)]
        paths = []

        if len(matching_files) > 0:
            for file in matching_files:
                paths.append(os.path.join(self.source_folder, file))
                self.log.info(f"Found matching file: {file}")
        return paths

    def execute(self, context):
        try:
            gcs_hook = GCSHook(gcp_conn_id=self.gcp_conn_id)
            bucket = gcs_hook.get_conn().bucket(self.gcs_bucket_name)
            ssh_hook = SSHHook(ssh_conn_id=self.sftp_conn_id)

            with ssh_hook.get_conn() as ssh_client:
                with ssh_client.open_sftp() as sftp_client:
                    report_object_paths = self._get_file(sftp_client)
                    if len(report_object_paths) < 1 and self.fail_on_missing_file:
                        raise ValueError("No matching files found")

                    for path in report_object_paths:
                        output_object = os.path.join(self.dest_folder or '', path.split("/")[-1])

                        with sftp_client.open(path, bufsize=32768) as remote_file:
                            blob = bucket.blob(f'{output_object}', chunk_size=262144)
                            blob.upload_from_file(remote_file)
                        self.log.info(f'File: {output_object} uploaded successfully')
                        if self.move_object:
                            sftp_client.remove(path)
                            self.log.info(f'File {path} deleted successfully.')
        except Exception as e:
            self.log.error(f"An error occurred during upload: {e}")
            raise
        finally:
            if 'sftp_client' in locals() and sftp_client:
                sftp_client.close()
            if 'ssh_client' in locals() and ssh_client:
                ssh_client.close()