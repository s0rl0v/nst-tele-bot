import json
import traceback
import os

from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

from handlers import *

api_key = os.environ['api_key']

bot = Bot(token=api_key)
dispatcher = Dispatcher(bot, None)

dispatcher.add_handler(CommandHandler('help', on_help_cmd_handler))
dispatcher.add_handler(MessageHandler(
    Filters.photo, on_photo_received_handler))


def is_s3_event(event):
    return not "body" in event


def handle_s3_event(event):
    filename = event["Records"][0]['s3']['object']['key']
    process_file(bot, filename)


def handle_api_event(event):
    dispatcher.process_update(
        Update.de_json(json.loads(event["body"]), bot))


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        # api-gateway-simple-proxy-for-lambda-input-format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    try:
        print(f'[INFO] Request to lambda is: {event}')

        if is_s3_event(event):
            handle_s3_event(event)
        else:
            handle_api_event(event)
    except Exception as e:
        print(f"Failed to process webhook: {e}")
        traceback.print_exc()
        return {"statusCode": 500}

    return {"statusCode": 200}
