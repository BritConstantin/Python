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
import sqlite3
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

"""
In version 3_0 I've try to remmebermain context fields to the db of users.
Users Db contains two tables: 
    messages - contain all incoming messages(cols: message_id, user_id, message)
    user_data - contain updated data about user(user_id, first_name, last_name, age, gender, experience) 
"""
# done: add new table user_data
# done: add method that will insert data in to user_data table
# done: add method that would return all users
# todo: finish the db_keyboard realization(db command handler)

# todo: add method that would filter all messages by user id, and count
# todo: add method that will read data for the user which asked for it
# todo: add error handling table(save handled exception with stacktrace
#       and message that affect it

# region Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion

# region Global variables declaration
db_name = Path(__file__).name[:-3]
user_data_table = 'main.user_data'

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
SELECTING, TYPING_COMMAND = range(3, 5)
reply_keyboard = [
    ['Age', 'Gender'],
    ['Number'],  # todo: check how to get user number
    ['Exit']
    ]
db_keyboard = [
    ['Show users'],
    ['Count my commands'],
    ['Count the user commands'],
    ['Use custom SELECT'],
    ['Close connection']
    ]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_db = ReplyKeyboardMarkup(db_keyboard, one_time_keyboard=True)


# endregion


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


# region     Handlers
def start(update: Update, context: CallbackContext) -> int:
    print('...' + start.__name__ + '()')
    save_message_to_db(update, context)

    reply = update.message.reply_text(
            "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
            "Why don't you tell me something about yourself?",
            reply_markup=markup,
            )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    print('...' + regular_choice.__name__ + '()')
    save_message_to_db(update, context)
    text = update.message.text
    context.user_data['choice'] = text
    print(context.user_data)

    reply = update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    print('...' + custom_choice.__name__ + '()')
    print(context.user_data)
    save_message_to_db(update, context)
    reply = update.message.reply_text(
            'Alright, please send me the category first, ' 'for example "Most impressive skill"'
            )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    print('...' + received_information.__name__ + '()')
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    print(context.user_data)
    save_message_to_db(update, context)
    reply = update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
            " on something.",
            reply_markup=markup,
            )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    print('...' + done.__name__ + '()')
    save_message_to_db(update, context)
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    reply = update.message.reply_text(
            f"I learned these facts about you: {facts_to_str(user_data)} Until next time!"
            )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    user_data.clear()
    return ConversationHandler.END


# endregion

# region DB methods
def save_message_to_db(update: Update, context: CallbackContext):
    print('...' + save_message_to_db.__name__ + '()', end='->')
    t = update.message.text
    user = update.message.from_user
    text = t if len(t) <= 30 else t[:30]
    print(f' {update.message.message_id} '
          f'user {user.full_name}({user.id}):"' + text + '"')

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
    # print('      √ the message saved to db')
    save_user_to_db(update, context)


def initiate_db():
    print('...' + initiate_db.__name__ + '()')
    db = DbWorker(db_name)
    db.drop_table(user_data_table)
    create_user_data_table()
    db.close_connection()


def create_user_data_table():
    print('...' + create_user_data_table.__name__ + '()')
    db = DbWorker(db_name)
    try:
        # print(">>create_user_data_table")
        db.exec("""CREATE TABLE IF NOT EXISTS main.user_data ( 
                    user_id integer not null primary key ,
                    first_name text, 
                    last_name text,
                    age text,
                    gender text,    
                    experience text)""")

    except sqlite3.OperationalError as e:
        print(e)  # self.create_table.__name__ +

    db.close_connection()


def save_user_to_db(update: Update, context: CallbackContext):
    print('...' + save_user_to_db.__name__ + '()')
    db = DbWorker(db_name)
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    age = context.user_data[reply_keyboard[0][0]] \
        if reply_keyboard[0][1] in context.user_data.keys() else 'NULL'
    gender = context.user_data[reply_keyboard[0][1]] \
        if reply_keyboard[0][1] in context.user_data.keys() else 'NULL'
    experience = context.user_data[reply_keyboard[1][0]] \
        if reply_keyboard[1][0] in context.user_data.keys() else 'NULL'
    exec_command = f""" INSERT or REPLACE INTO {user_data_table} 
                 VALUES ( {user_id},
                         '{first_name}',
                         '{last_name}',
                         '{age}',
                         '{gender}',
                         '{experience}'
            )"""

    db.exec(exec_command)
    db.close_connection()


# endregion

# region markup_db handlers

def db_start(update: Update, context: CallbackContext):
    print('...' + db_start.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)
    reply = update.message.reply_text(
            "Hi! \n You enter in DB mode",
            reply_markup=markup_db,
            )

    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    return SELECTING


def show_users(update: Update, context: CallbackContext):
    print('...' + show_users.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)
    db = DbWorker(db_name)
    users = db.get_all_table_rows(user_data_table)

    message_counter = 1
    for s in users:
        reply = update.message.reply_text(f'{users.index(s)}|{s[2]} {s[1]}|{s[0]}')
        bot_update = Update(update_id=update.update_id + message_counter, message=reply)
        message_counter = +1
        save_message_to_db(bot_update, context)

    reply2 = reply.reply_text("That is all users", reply_markup=markup_db)
    bot_update = Update(update_id=update.update_id + message_counter, message=reply2)
    save_message_to_db(bot_update, context)

    return SELECTING


def count_my_commands(update: Update, context: CallbackContext):
    print('...' + count_my_commands.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)


def count_the_user_commands(update: Update, context: CallbackContext):
    print('...' + count_the_user_commands.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)


def use_custom_select(update: Update, context: CallbackContext):
    print('...' + use_custom_select.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)


def close_connection(update: Update, context: CallbackContext):
    print('...' + close_connection.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)


def execute_custom_command(update: Update, context: CallbackContext):
    print('...' + execute_custom_command.__name__ + '()')
    save_message_to_db(update, context)
    print(context.user_data)


# endregion

def main() -> None:
    print('...' + main.__name__ + '()')
    initiate_db()
    updater = Updater(conversation_3_0_bot_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                CHOOSING: [
                    MessageHandler(Filters.regex(f'^({reply_keyboard[0][0]}|{reply_keyboard[0][1]})$'),
                                   regular_choice),
                    MessageHandler(Filters.regex(f'^({reply_keyboard[1][0]})$'), custom_choice),
                    ],
                TYPING_CHOICE: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(f'^({reply_keyboard[2][0]})$')),
                                   regular_choice)
                    ],
                TYPING_REPLY: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex(f'^({reply_keyboard[2][0]})$')),
                                   received_information)
                    ],
                },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
            )

    db_handler = ConversationHandler(
            entry_points=[CommandHandler('db', db_start)],
            states={
                SELECTING: [
                    MessageHandler(Filters.regex(f'^(Show users)$'), show_users),
                    MessageHandler(Filters.regex(f'^({db_keyboard[1]})$'), count_my_commands),
                    MessageHandler(Filters.regex(f'^({db_keyboard[2]})$'), count_the_user_commands),
                    MessageHandler(Filters.regex(f'^({db_keyboard[3]})$'), use_custom_select)
                    ],
                TYPING_COMMAND: [
                    MessageHandler(Filters.text & ~Filters.command, execute_custom_command)
                    ],
                # TYPING_REPLY: [
                #     MessageHandler(Filters.text & ~(Filters.command | Filters.regex(done_str)),
                #                    received_information)
                #     ],
                },
            fallbacks=[
                MessageHandler(Filters.regex(f'^({db_keyboard[4]})$'), close_connection)],
            )
    dispatcher.add_handler(db_handler)

    # the handler would handle all metssages that would not handled by others and save to the DB
    db_save_handler = MessageHandler(Filters.text | Filters.command, save_message_to_db)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(db_save_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
