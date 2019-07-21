import os

from datetime import datetime
import botocore
import boto3

KEYS = ['imagenet-vgg-verydeep-19.mat',
        f'content.{os.environ["SESSION_ID"]}.jpg', 'style.jpg']
TEMP_BUCKET = os.environ["BUCKET_NAME"]

s3 = boto3.resource('s3')

try:
    step = datetime.now()
    for key in KEYS:
        s3.Bucket(TEMP_BUCKET).download_file(key, key)
    print(f'Elapsed time: {datetime.now() - step}')
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == '404':
        print('The object does not exist.')
    else:
        raise
