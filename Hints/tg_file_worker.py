import logging
import os

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
        # FIXME: add check of other types
        if self.file_type == 'document':
            self.fill_document_fields()
        else:
            self.log.error(f' \n ERROR \n File type {self.file_type} is not supported')
            raise NotImplementedError

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
        if "photo" in message.to_dict():
            file_type = "photo"
        if "video" in message.to_dict():
            file_type = "video"
        if "video_note" in message.to_dict():
            file_type = "video_note"
        if "invoice" in message.to_dict():
            file_type = "invoice"
        if "document" in message.to_dict():
            file_type = "document"
        return file_type

    def fill_document_fields(self):
        self.tg_file_name = self.message.document.file_name
        self.file_id = self.message.document.file_id
        self.file_size = self.message.document.file_size
        self.mime_type = self.message.document.mime_type
        self.file_unique_id = self.message.document.file_unique_id

    def __str__(self) -> str:
        return '\ttg_file_name: {}\n' \
               '\tfile_size: {}\n' \
               '\tmime_type: {}\n' \
               '\tfile_type: {}'.format(self.tg_file_name, self.file_size, self.mime_type, self.file_type)

    def download_file(self, bot: Bot, path: str = "", attempts: int = 0):
        # TODO: fix implementation of download method by adding custom path
        # TODO: add something to prevent any injections with the file names
        # if path == "":
        #     path = "/downloaded_files"

        self.actual_file_name = bot.getFile(file_id=self.file_id).download()
        self.log.info(' File "{}" downloaded with name "{}"'.format(self.tg_file_name, self.actual_file_name))
        if attempts == 0:
            attempts == ''

        try:
            os.rename(r'{}'.format(self.actual_file_name),
                      r'{}{}'.format(attempts, self.tg_file_name)
                      )
            self.log.info(' File "{}" renamed "{}"'.format(self.actual_file_name, self.tg_file_name))
        except FileExistsError as e:
            self.log.error('''
            ERROR - FileExistsError 
            File "{}" wasn't renamed because of 
            {}'''.format(self.actual_file_name, e))
            self.actual_file_name =('{}{}'.format(attempts, self.tg_file_name))
            attempts += 1
            self.download_file(bot,attempts=attempts)
