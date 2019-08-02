import os
import boto3
from functools import wraps

from utils.base import Singleton
from utils.constants import *


class DynamoContextSingleton(metaclass=Singleton):
    def __init__(self):
        self.table = boto3.resource('dynamodb').Table(
            os.environ['ACCESS_TABLE'])

    def add_user(self, user_id):
        self.table.put_item(Item={'id': int(user_id)})

    def delete_user(self, id):
        raise NotImplementedError

    def get_user(self, user_id):
        resp = self.table.get_item(Key={'id': int(user_id)})
        if "Item" in resp:
            return resp["Item"]
        else:
            return None

    def list_users(self):
        raise NotImplementedError


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        trusted = DynamoContextSingleton().get_user(user_id)
        if not trusted:
            print("Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text(ACCESS_DENIED_TEXT)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped
