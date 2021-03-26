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
logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


# endregion

def initiate_db():
    log.info('...' + initiate_db.__name__ + '()')
    try:
        db = DbWorker(db_name, 1)
        db.create_table(messages_table_name, messages_table_format)
        db.create_table(user_data_table_name, user_data_table_format)
        db.create_table(files_table_name, files_table_format)
        db.close_connection()
    except Exception as e:
        log.exception(f' Exception is in {initiate_db.__name__}(): \n{e}')
def start(update:Update,  context: CallbackContext) -> int:
    log.info('...' + start.__name__ + '()')


def main() -> None:
    log.info('...' + main.__name__ + '()')
    initiate_db()
    updater = Updater(file_storage_1_2_Bot)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={},
        fallbacks=[],
            )
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
