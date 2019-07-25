import os
import io
import boto3
import botocore

CONTENT = 'content'
GENERATED = 'generated'
STYLE = 'style'

BUCKET_NAME = os.environ['bucket_name']

s3 = boto3.resource('s3')
batch = boto3.client('batch')


def process_generated(bot, filename):
    print(f"Processing {filename}")
    _, chat_id, _ = filename.split('.')

    file_stream = download_file_from_s3(filename)

    bot.send_photo(chat_id=chat_id, photo=file_stream)


def process_content(bot, filename):
    print(f"Processing {filename}")
    _, chat_id, _ = filename.split('.')
    submit_job_response = batch.submit_job(
        jobName=f'nst-{chat_id}',
        jobQueue=os.environ['job_queue'],
        jobDefinition=os.environ['job_definition'],
        containerOverrides={'environment': [
            {'name': 'SESSION_ID', 'value': chat_id},
            {'name': 'BUCKET_NAME', 'value': BUCKET_NAME}
        ]}
    )


def process_file(bot, filename):
    print(f"Processing s3 event, filename is {filename}")
    image_type, _, _ = filename.split('.')

    if image_type == GENERATED:
        process_generated(bot, filename)
    elif image_type == CONTENT:
        process_content(bot, filename)


def download_file_from_telegram(bot, file_id):
    file_bytes = io.BytesIO()
    file = bot.get_file(file_id)
    file.download(out=file_bytes)
    file_bytes.seek(0)
    return file_bytes


def upload_file_to_s3(file_bytes, bucket_name, filename):
    object = s3.Object(bucket_name, filename)
    object.put(Body=file_bytes)


def download_file_from_s3(filename):
    bucket = s3.Bucket(BUCKET_NAME)
    object = bucket.Object(filename)

    file_stream = io.BytesIO()
    object.download_fileobj(file_stream)
    file_stream.seek(0)
    return file_stream


def on_help_cmd_handler(bot, update):
    update.message.reply_text(
        "Please send an image - the bot will run a Neural Style Transfer algorithm on it and will send you a result as soon as possible. \
            Currently, only the built-in style image below is supported - so all the images you will send to the bot will be of some style, one way or another.")
    bot.send_photo(chat_id=update.message.chat_id,
                   photo=download_file_from_s3(f'{STYLE}.jpg'))


def on_photo_received_handler(bot, update):
    image_file_id = update.message.photo[-1].file_id
    chat_id = update.message.chat_id

    file_bytes = download_file_from_telegram(bot, image_file_id)
    upload_file_to_s3(
        file_bytes, BUCKET_NAME, f'{CONTENT}.{chat_id}.jpg')

    print(f"Image from {chat_id} chat has been uploaded")
    update.message.reply_text(
        "Thanks! I've started style transfer, please wait a bit - this could take long time (~10 min).")
