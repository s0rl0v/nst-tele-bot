import boto3
import os

from utils.constants import *
from utils.s3_helper import S3FileHelperSingleton
from utils.bot_ext import BotExtSingleton


class S3EventHandler:
    def __init__(self):
        self.batch = boto3.client('batch')

    def process_generated(self, filename):
        print(f"Processing {filename}")
        _, chat_id, _ = filename.split('.')

        file_stream = S3FileHelperSingleton().download_file_from_s3(filename)

        BotExtSingleton().send_photo(chat_id=chat_id, photo=file_stream)

    def process_content(self, filename):
        print(f"Processing {filename}")
        _, chat_id, _ = filename.split('.')
        submit_job_response = self.batch.submit_job(
            jobName=f'nst-{chat_id}',
            jobQueue=os.environ['job_queue'],
            jobDefinition=os.environ['job_definition'],
            containerOverrides={'environment': [
                {'name': 'SESSION_ID', 'value': chat_id},
                {'name': 'BUCKET_NAME', 'value': S3FileHelperSingleton().bucket_name}
            ]}
        )

    def process_file(self, filename):
        print(f"Processing s3 event, filename is {filename}")
        image_type, _, _ = filename.split('.')

        if image_type == GENERATED:
            self.process_generated(filename)
        elif image_type == CONTENT:
            self.process_content(filename)
