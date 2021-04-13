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
from Hints.tg_file_worker import TgFileWorker

# done: finish db creation
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
    update.message.from_user.send_message("now you send to my file and I'll try to save it")

    return LOGGED_IN


def start(update: Update, context: CallbackContext) -> int:
    log.info('...' + start.__name__ + '()')
    update.message.from_user.send_message("Hi username! \n availible commands are:\n /savefile")
    return LOGGED_IN




def received_doc(update: Update, context: CallbackContext) -> int:
    log.info('...' + received_doc.__name__ + '()')
    log.info(update.message.to_json())
    try:
        file_type = TgFileWorker.get_file_type(message=update.message)
        the_file = TgFileWorker(update.message)
        log.info(f' The file:\n{the_file}')
        the_file.download_file(updater.bot)

        update.message.from_user.send_message(f"you send me doc {the_file.tg_file_name}")
    except NotImplementedError as e:
        update.message.from_user.send_message(f"Error while handling file apperared\n{e}")
        log.error(f'{received_doc.__name__} raise the NotImplementedError' )
        log.error(e)
    # except FileExistsError as e:
    #     update.message.from_user.send_message(f"FileExistsError while handling file apperared\n{e}")
    #     log.error(f'FileExistsError ERROR ')
    #     log.error(e)
    # if '"audio": {"file_id"' in update.message.to_json():
    #     file = update.message.audio
    #     file_id = file.file_id
    #     file_name = file.file_name
    #     file_size = file.file_size
    #     mime_type = file.mime_type
    #     local_file_name = updater.bot.getFile(file_id=file_id).download()
    #     log.info(f' File "{local_file_name}" downloaded')
    #
    #     file_name = f'{update.message.audio.file_name} ({update.message.audio.mime_type})'
    # else:
    #     file_name = "Not handled"
    #     print(update.message.to_json())


    return LOGGED_IN


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
                MessageHandler(Filters.document | Filters.audio | Filters.photo, received_doc),
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
