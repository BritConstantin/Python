import logging
from pathlib import Path
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
    )
from Hints.db_worker import DbWorker
from bot_info import file_storage_1_2_Bot
from db_data import *
# TODO: finish db creation
# region var declaration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

# endregion

def initiate_db():
    log.info('...' + initiate_db.__name__ + '()')


def main() -> None:
    log.info('...' + main.__name__ + '()')
    initiate_db()
    updater = Updater(file_storage_1_2_Bot)



if __name__ == '__main__':
    main()
