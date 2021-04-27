import logging
import os
import time

import telegram
from telegram import message as tgm, Bot
from telegram.ext import Updater

from bots.file_storage_bot.db_data import files_table_format


class TgFile:
    def __init__(self, message: telegram.message, file_type=None, loglevel=logging.INFO):
        logging.basicConfig()
        logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.level = loglevel
        self.log.info('...TgFileWorker.__inin__()')

        self.message = message
        self.actual_file_name = ""
        self.tg_file_name = ""
        self.file_type = TgFile.get_file_type(message)
        self.file_id = ""
        self.file_unique_id = ""
        self.file_unique_id_dict = dict()
        self.mime_type = ""
        self.file_size = -1
        self.duration = 0
        self.performer = ""
        self.title = ""
        self.creation_time = self.message.date
        # TODO: 1 add ability to work with photos(wip)
        # TODO: 1 add any sender info
        # TODO: 2 add check of all types(
        #     done: document,
        #           audio,
        #           video)
        if self.file_type == 'document':
            self.fill_document_fields()
        elif self.file_type == 'audio':
            self.fill_audiot_fields()
        elif self.file_type == 'photo':  # WIP
            self.fill_photo_fields()
        elif self.file_type == 'video':
            self.fill_video_fields()
        else:
            self.log.error(f' \n ERROR \n File type {self.file_type} is not supported')
            raise NotImplementedError

    @staticmethod
    def get_file_type(message: telegram.message) -> str:
        # done: 1 fix problem with detecting.txt files like photo file
        # FIXME: 2 add ability to handle
        #  video_note
        #  animation
        #  voice
        #  invoice
        #  video -> done
        #  audio -> done
        #  photo -> done
        #  document -> done

        file_type = None
        # if "animation" in message.to_json():
        #     file_type = "animation"
        if '"audio": {"file_id":' in message.to_json():
            file_type = "audio"
        # if "caption"in message.to_json():
        #     file_type = "caption"
        if '"photo": [{"file_id":' in message.to_json():
            file_type = "photo"
        if '"video": {"file_id"' in message.to_json():
            file_type = "video"
        # if "video_note"in message.to_json():
        #     file_type = "video_note"
        # if "invoice"in message.to_json():
        #     file_type = "invoice"
        if '"document": {"file_id"' in message.to_json():
            file_type = "document"

        return file_type

    def fill_document_fields(self):
        self.tg_file_name = self.message.document.file_name
        self.file_id = self.message.document.file_id
        self.file_size = self.message.document.file_size
        self.mime_type = self.message.document.mime_type
        self.file_unique_id = self.message.document.file_unique_id

    def fill_audiot_fields(self):
        """
        "audio": {
            "file_id": "CQACAgIAAxkBAAIBV2B1jv60SxrFVCMxCzBL0F4GIcHZAAK6CwACW1MwS-9XTxDr-In0HgQ",
            "file_unique_id": "AgADugsAAltTMEs",
            "duration": 175,
            "performer": "\u0421\u043a\u0440\u0438\u043f\u0442\u043e\u043d\u0438\u0442",
            "title": "...\u0418\u043d\u0441\u0442\u0443",
            "file_name": "15. ...\u0418\u043d\u0441\u0442\u0443.mp3",
            "mime_type": "audio/mp3",
            "file_size": 7377897},
        :return:
        """
        self.file_id = self.message.audio.file_id
        self.file_unique_id = self.message.audio.file_unique_id
        self.duration = self.message.audio.duration
        self.performer = self.message.audio.performer
        self.title = self.message.audio.title
        self.tg_file_name = self.message.audio.file_name
        self.mime_type = self.message.audio.mime_type
        self.file_size = self.message.audio.file_size

    def download_file(self, bot: Bot, path: str = "", attempts: int = 0):
        # TODO: 3 fix implementation of download method by adding custom path
        # TODO: 5 add something to prevent any injections with the file names
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
            self.actual_file_name = ('{}{}'.format(attempts, self.tg_file_name))
            attempts += 1
            self.download_file(bot, attempts=attempts)

    def fill_video_fields(self):
        '''
            "video": {
        "file_id": "BAACAgIAAxkBAAIBp2B5KK_LS-cl2oKnJJk_Y_nDYClKAAIaDAACB-uwSwEh5PrlHCP9HwQ",
        "file_unique_id": "AgADGgwAAgfrsEs",
        "width": 1080,
        "height": 1920,
        "duration": 8,
        "thumb": {
            "file_id": "AAMCAgADGQEAAgGnYHkor8tL5yXagqckmT9j-cNgKUoAAhoMAAIH67BLASHk-uUcI_2A-E-kLgADAQAHbQADdDoAAh8E",
            "file_unique_id": "AQADgPhPpC4AA3Q6AAI",
            "width": 180,
            "height": 320,
            "file_size": 14130
            },
        "mime_type": "video/mp4",
        "file_size": 18153228},
        :return:
        '''
        self.file_id = self.message.video.file_id
        self.file_unique_id = self.message.video.file_unique_id
        self.width = self.message.video.width
        self.height = self.message.video.height
        self.duration = self.message.video.duration
        if 'thumb' in self.message.video.to_json():
            self.thumb = self.message.video.thumb
            self.thumb.file_id = self.message.video.thumb.file_id
            self.thumb.file_unique_id = self.message.video.thumb.file_unique_id
            self.thumb.width = self.message.video.thumb.width
            self.thumb.height = self.message.video.thumb.height
            self.thumb.file_size = self.message.video.thumb.file_size
        self.tg_file_name = f'video_{int(round(time.time() * 1000))}'
        self.mime_type = self.message.video.mime_type
        self.file_size = self.message.video.file_size

    def get_db_format_data(self) -> dict:
        d = files_table_format.copy()
        for attr, value in self.__dict__.items():
            # print(f'    {attr} = {value}')
            if attr in d.keys():
                # print(f'+++{attr}')
                d[attr] = value
            else:
                # print(f'---{attr}')
                d[attr] = ""

        return d

    def __str__(self) -> str:
        return '\ttg_file_name: {}\n' \
               '\tfile_size: {}\n' \
               '\tmime_type: {}\n' \
               '\tfile_type: {}'.format(self.tg_file_name,
                                        self.file_size,
                                        self.mime_type,
                                        self.file_type)

    def __repr__(self) -> str:
        m = ""
        for i in self.message.to_json().split(': {'):
            m = f'{i} \n\n'
        return f'''
        message  = "{m}"
        actual_file_name = "{self.actual_file_name}"
        tg_file_name = "{self.tg_file_name}"
        file_type = "{self.file_type}"
        file_id = "{self.file_id}"
        file_unique_id = "{self.file_unique_id}"
        file_unique_id_dict = "{self.file_unique_id_dict}"
        mime_type = "{self.mime_type}"
        file_size = "{self.file_size}"
        duration = "{self.duration}"
        performer = "{self.performer}"
        title = "{self.title}"
        width = "{self.width}"
        height = "{self.height}"
        '''

# done: 1 create file name in case of video file
