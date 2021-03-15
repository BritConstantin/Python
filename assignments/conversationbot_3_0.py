#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
"""
In version 3_0 I've try to remmebermain context fields to the db of users.
Users Db contains two tables: 
    messages - contain all incoming messages(cols: message_id, user_id, message)
    user_data - contain updated data about user(user_id, first_name, last_name, age, gender, experience) 
"""
# done: add new table user_data
# todo: add method that whould filter all messages by user id
# todo: add method that will insert data in to user_data table
# todo: add method that will read data for the user wich asked for it
# todo: add error handling table(save handled exeption with stacktrace
#       and message that affecte it
import logging
from pathlib import Path
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    )

from Hints.db_worker import DbWorker
from bot_info import conversation_3_0_bot_TOKEN

# region Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion

# region Global variables declaration
db_name = Path(__file__).name[:-3]
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [
    ['Age', 'Gender'],
    ['Show Exp', 'Show Lvl'],
    ['Exit']
    ]
"""user_id integer not null primary key ,
                      first_name text, 
                      last_name text,
                      age text,
                      gender text,    
                      experience text"""
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# endregion


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


# region     Handlers
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
            "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
            "Why don't you tell me something about yourself?",
            reply_markup=markup,
            )
    print('Context:')
    print(context)
    print('Update:')
    print(update)

    print('User:')
    print(update['message']['chat'])

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text

    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
            'Alright, please send me the category first, ' 'for example "Most impressive skill"'
            )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
            " on something.",
            reply_markup=markup,
            )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
            f"I learned these facts about you: {facts_to_str(user_data)} Until next time!"
            )
    update.message.reply_text(str(user_data))
    print(context)
    user_data.clear()
    return ConversationHandler.END


# endregion

# region DB methods
def save_message_to_db(update: Update, context: CallbackContext, ):
    user = update.message.from_user
    print(f'-> catch message {update.message.message_id} '
          f'from user {user.id}({user.full_name}):')
    print('->>' + update.message.text)

    db = DbWorker(db_name)  # db name created from the file name

    table_name = 'messages'
    users_hat = {
        'message_id': 'integer',
        'user_id': 'integer',
        'message': 'string'
        }

    db.create_table(table_name, users_hat)
    db.insert_row(table_name, users_hat.keys(),
                  (update.message.message_id,
                   user.id,
                   update.message.to_json()))
    db.close_connection()


def initiate_db():
    db = DbWorker(db_name)
    db.create_user_data_table()
    db.close_connection()


# endregion

def main() -> None:
    initiate_db()
    updater = Updater(conversation_3_0_bot_TOKEN)

    dispatcher = updater.dispatcher
    db_save_handler = MessageHandler(Filters.text | Filters.command, save_message_to_db)
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                CHOOSING: [
                    MessageHandler(Filters.regex('^(Age|Favourite colour|Number of siblings)$'),
                                   regular_choice),
                    MessageHandler(Filters.regex('^Something else...$'), custom_choice),
                    ],
                TYPING_CHOICE: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice)
                    ],
                TYPING_REPLY: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                                   received_information, )
                    ],
                },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
            )

    dispatcher.add_handler(db_save_handler)
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
