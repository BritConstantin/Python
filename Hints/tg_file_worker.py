import logging

import telegram
from telegram import message as tgm, Bot
from telegram.ext import Updater


class TgFileWorker:

    def __init__(self, message: telegram.message, file_type=None, loglevel=logging.INFO):
        logging.basicConfig()
        logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.level = loglevel
        self.log.info('...TgFileWorker.__inin__()')

        self.message = message
        self.actual_file_name = ""
        self.tg_file_name = ""
        self.file_type = TgFileWorker.get_file_type(message)
        self.file_id = ""
        self.file_unique_id = ""
        self.file_unique_id_dict = dict()
        self.mime_type = ""
        self.file_size = -1
        if self.file_type != 'photo':
            self.fill_document_fields()
        else:
            self.log.error(f' File type {self.file_type} is not supported')

    @staticmethod
    def get_file_type(message: telegram.message) -> str:
        # fixme: fix problem with detecting.txt files like photo file
        file_type = None
        if "animation" in message.to_dict():
            file_type = "animation"
        if "audio" in message.to_dict():
            file_type = "audio"
        if "caption" in message.to_dict():
            file_type = "caption"
        if "document" in message.to_dict():
            file_type = "document"
        if "photo" in message.to_dict():
            file_type = "photo"
        if "invoice" in message.to_dict():
            file_type = "invoice"
        if "video" in message.to_dict():
            file_type = "video"
        if "video_note" in message.to_dict():
            file_type = "video_note"

        return file_type

    def fill_document_fields(self):
        self.tg_file_name = self.message.document.file_name
        self.file_id = self.message.document.file_id
        self.file_size = self.message.document.file_size
        self.mime_type = self.message.document.mime_type
        self.file_unique_id = self.message.document.file_unique_id

        # FIXME: fix emplementation of download method by adding custom path

    def __str__(self) -> str:
        return '\ttg_file_name: {}\n' \
               '\tfile_size: {}\n' \
               '\tmime_type: {}\n' \
               '\tfile_type: {}'.format(self.tg_file_name, self.file_size, self.mime_type, self.file_type)

    def download_file(self, bot: Bot, path: str = ""):
        if path == "":
            path = "/downloaded_files"

        the_file =  bot.getFile(file_id=self.file_id)
        print(the_file)
        self.actual_file_name =the_file.download()
        self.log.info(' File "{}" downloaded with name "{}"'.format(self.tg_file_name, self.actual_file_name))
