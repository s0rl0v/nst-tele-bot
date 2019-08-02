import os
import boto3
import botocore

from utils.constants import *
from utils.s3_helper import S3FileHelperSingleton
from utils.access import DynamoContextSingleton, restricted


@restricted
def on_users_handler(bot, update):
    arr = update.message.text.split()

    try:
        assert len(arr) == 2
        assert isinstance(arr[1], int)
    except Exception as e:
        update.message.reply_text(INCORRECT_USER_FORMAT)
        return

    user_id = int(arr[1])

    DynamoContextSingleton().add_user(user_id)
    print(USER_ADDED.format(user_id))
    update.message.reply_text(USER_ADDED.format(user_id))


def on_help_cmd_handler(bot, update):
    update.message.reply_text(HELP_TEXT)
    bot.send_photo(chat_id=update.message.chat_id,
                   photo=S3FileHelperSingleton().download_file_from_s3(f'{STYLE}.jpg'))


@restricted
def on_photo_received_handler(bot, update):
    image_file_id = update.message.photo[-1].file_id
    chat_id = update.message.chat_id

    file_bytes = bot.download_file_from_telegram(image_file_id)
    S3FileHelperSingleton().upload_file_to_s3(
        file_bytes, f'{CONTENT}.{chat_id}.jpg')

    print(IMAGE_UPLOADED_TEXT.format({chat_id}))
    update.message.reply_text(PROCESSING_IN_PROGRESS_TEXT)
