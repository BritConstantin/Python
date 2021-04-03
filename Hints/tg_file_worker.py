import logging

import telegram
from telegram import message as tgm


class TgFileWorker:

    def __init__(self, message: telegram.message, file_type=None, loglevel=logging.INFO):
        logging.basicConfig()
        logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.level = loglevel

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
            self = self.fill_document_fields()
        else:
            self.log.error(f' File type {self.file_type} is not supported')

    @staticmethod
    def get_file_type(self, message: telegram.message) -> str:
        if "animation" in message.to_dict():
            self.file_type = "animation"
        if "audio" in message.to_dict():
            self.file_type = "audio"
        if "caption" in message.to_dict():
            self.file_type = "caption"
        if "document" in message.to_dict():
            self.file_type = "document"
        if "photo" in message.to_dict():
            self.file_type = "photo"
        if "invoice" in message.to_dict():
            self.file_type = "invoice"
        if "video" in message.to_dict():
            self.file_type = "video"
        if "video_note" in message.to_dict():
            self.file_type = "video_note"

        self.log.info(f"{self.file_type} found")

        return self.file_type

    def fill_document_fields(self):
        self.tg_file_name = self.message.document.file_name
        self.file_id = self.message.document.file_id
        # FIXME: finish implementation

