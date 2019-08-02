import io
import os
import boto3

from utils.base import Singleton


class S3FileHelperSingleton(metaclass=Singleton):
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.bucket_name = os.environ['bucket_name']
        self.bucket = self.s3.Bucket(self.bucket_name)

    def upload_file_to_s3(self, file_bytes, filename):
        object = self.s3.Object(self.bucket_name, filename)
        object.put(Body=file_bytes)

    def download_file_from_s3(self, filename):
        file_stream = io.BytesIO()
        obj_handle = self.bucket.Object(filename)

        obj_handle.download_fileobj(file_stream)
        file_stream.seek(0)

        return file_stream
