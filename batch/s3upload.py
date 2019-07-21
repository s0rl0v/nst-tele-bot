import os
import boto3
import botocore

from datetime import datetime

KEY = f'generated.{os.environ["SESSION_ID"]}.jpg'
TEMP_BUCKET = os.environ["BUCKET_NAME"]

s3 = boto3.resource('s3')

try:
    print(f'Uploading file {KEY} to bucket {TEMP_BUCKET}')
    step = datetime.now()
    s3.Bucket(TEMP_BUCKET).upload_file(KEY, KEY)
    print(f'Bucket uploaded in {datetime.now() - step}')
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == '404':
        print('The object does not exist.')
    else:
        raise
