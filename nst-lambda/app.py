import json
import traceback
import os

from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackQueryHandler, CommandHandler

from utils.base import *
from utils.s3_event_handler import *
from utils.handlers import *


@LambdaHandler
class MyLambdaClass(LambdaBase):
    def __init__(self):
        self.dispatcher = Dispatcher(BotExtSingleton(), None)

        self.dispatcher.add_handler(
            CommandHandler('help', on_help_cmd_handler))
        self.dispatcher.add_handler(MessageHandler(
            Filters.photo, on_photo_received_handler))
        self.dispatcher.add_handler(CommandHandler('users', on_users_handler))
        self.s3_handler = S3EventHandler()

    def __is_s3_event(self, event):
        return not "body" in event

    def __handle_s3_event(self, event):
        filename = event["Records"][0]['s3']['object']['key']
        self.s3_handler.process_file(filename)

    def __handle_api_event(self, event):
        self.dispatcher.process_update(
            Update.de_json(json.loads(event["body"]), BotExtSingleton()))

    def handle(self, event, context):
        try:
            print(f'[INFO] Request to lambda is: {event}')

            if self.__is_s3_event(event):
                self.__handle_s3_event(event)
            else:
                self.__handle_api_event(event)
        except Exception as e:
            print(f"Failed to process webhook: {e}")
            traceback.print_exc()
            return {"statusCode": 500}

        return {"statusCode": 200}
