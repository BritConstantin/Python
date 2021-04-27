import logging
from pathlib import Path

import telegram
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, File
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
from bots.file_storage_bot.db_data import *
from Hints.tg_file_worker import TgFile

# done: finish db creation
# TODO: 1 add ability to save files in db after creation WIP
# TODO: 1.2 add ability to send any file from db to user
# TODO: 1.3 add abitlity to store 10 files for a user

# region var declaration
logging.basicConfig(format='%(asctime)s|%(name)s|%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

LOGGED_IN = range(0, 1)
updater = Updater(file_storage_1_2_Bot)


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


def save_file(update: Update, context: CallbackContext) -> int:
    log.info('...' + save_file.__name__ + '()')
    update.message.from_user.send_message("now you send to me file and I'll try to save it")

    return LOGGED_IN


def start(update: Update, context: CallbackContext) -> int:
    log.info('...' + start.__name__ + '()')
    update.message.from_user.send_message("Hi username! \n availible commands are:\n /savefile")
    return LOGGED_IN


def received_doc(update: Update, context: CallbackContext) -> int:
    log.info('...' + received_doc.__name__ + '()')
    log.info(update.message.to_json())
    try:
        file_type = TgFile.get_file_type(message=update.message)
        the_file = TgFile(update.message)
        log.info(f' The file:\n{the_file}')
        the_file.download_file(updater.bot)
        write_to_db(the_file)
        update.message.from_user.send_message(f"you send me doc {the_file.tg_file_name} \n{the_file.__repr__()}")
    except NotImplementedError as e:
        update.message.from_user.send_message(
                f"Error while handling a file apperared\nNotImplementedError\n{e}")
        log.error(f'{received_doc.__name__} raise the NotImplementedError')
        log.error(e)
    except Exception as e:
        update.message.from_user.send_message(
                f"Error while handling a file apperared\nUnknownError\n"
                f"☻Please contact with the administrator {e}")
        log.error(f'{received_doc.__name__} raise the NotImplementedError')
        log.error(e)

    return LOGGED_IN


# TODO: WIP update db table to be able save all fieds that wer given
#       in files_table_format
def write_to_db(the_file: TgFile):
    log.info('...' + initiate_db.__name__ + '()')
    try:
        db = DbWorker(db_name, 1)
        # TODO: 2 do I actually need new new method every time I whant to save something in db?
        db.save_tg_file(files_table_name,  the_file.get_db_format_data())

        db.close_connection()
    except Exception as e:
        log.exception(f' Exception is in {initiate_db.__name__}(): \n{e}')


#
# def save_message_to_db(update: Update, context: CallbackContext):
#     print('...' + save_message_to_db.__name__ + '()', end='->')
#     user = update.message.from_user
#     if 'text' in update.message.to_dict():
#         t = update.message.text
#         text = t if len(t) <= 25 else t[:25]
#     else:
#         text = update.message.to_json()
#     print(f' {update.message.message_id} '
#           f'user {user.full_name}({user.id}):"' + text + '"')
#
#     db = DbWorker(db_name)
#
#     db.create_table(messages_table_name, user_data_table_format)
#     db.save_message(messages_table_name,
#                     (update.message.message_id,
#                      user.id,
#                      update.message.to_json()))
#     db.close_connection()
#     # print('      √ the message saved to db')
#     # save_user_to_db(update, context)


def main() -> None:
    log.info('...' + main.__name__ + '()')
    initiate_db()
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                LOGGED_IN: [
                    CommandHandler('savefile', save_file),
                    MessageHandler(Filters.document |
                                   Filters.photo |
                                   Filters.audio |
                                   Filters.dice |
                                   Filters.invoice |
                                   Filters.location |
                                   Filters.video |
                                   Filters.video_note |
                                   Filters.animation |
                                   Filters.voice
                                   , received_doc),
                    ]
                },
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
