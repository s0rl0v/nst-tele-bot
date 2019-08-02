import os
import io

from utils.base import Singleton
from telegram import Bot


class BotExtSingleton(Bot, metaclass=Singleton):
    def __init__(self):
        super().__init__(os.environ['api_key'])

    def download_file_from_telegram(self, file_id):
        file_bytes = io.BytesIO()
        file = self.get_file(file_id)
        file.download(out=file_bytes)
        file_bytes.seek(0)
        return file_bytes
