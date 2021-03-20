
import sqlite3
import logging
from pathlib import Path
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
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

# done: add new table user_data
# done: add method that will insert data in to user_data table
# done: add method that would return all users
# todo: finish the db_keyboard realization(db command handler)
# todo: check how to get user number
# todo: add method that would filter all messages by user id, and count
# todo: add method that will read data for the user which asked for it
# todo: add error handling table(save handled exception with stacktrace
#       and message that affect it
# todo: study how to use logger correct
#          logger.info(
#         "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
#     )
# todo: learn how to work with pickling

# region Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion

# region Global variables declaration
db_name = Path(__file__).name[:-3]
user_data_table = 'main.user_data'

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
reply_keyboard = [
    [KeyboardButton('Age'), KeyboardButton('Gender')],
    [KeyboardButton('Number', request_contact=True)],  # todo: check how to get user number
    [KeyboardButton('Exit')]
]
markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, one_time_keyboard=True, )
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
    print('contact' in update.message.to_dict().keys())

    reply = update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why dont you tell me something about yourself?",
        reply_markup=markup
    )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    print('...' + regular_choice.__name__ + '()')
    save_message_to_db(update, context)
    text = update.message.text
    context.user_data['choice'] = text
    print(context)

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
        f"Done: {facts_to_str(user_data)} Until next time!"
    )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    user_data.clear()
    return ConversationHandler.END


def fallbacks(update: Update, context: CallbackContext) -> int:

    print('...' + save_contact.__name__ + '()')
    save_message_to_db(update, context)

    return ConversationHandler.END


def save_contact(update: Update, context: CallbackContext):
    print('...' + save_contact.__name__ + '()')
    save_message_to_db(update, context)
    if 'phone_number' in update.message:
        update.message.reply_text("Thank you for trust")
    else:
        update.message.reply_text("It's sad, but you decide not to give me your contacts")
    return CHOOSING


# endregion

# region DB methods
def save_message_to_db(update: Update, context: CallbackContext):
    print('...' + save_message_to_db.__name__ + '()', end='->')
    user = update.message.from_user
    if 'text' in update.message.to_dict():
        print('text is in the message')
        t = update.message.to_json()
        text = t #if len(t) <= 30 else t[:30]
    else:
        print('-->> ther is no text in the message!!')
        text = update.message.to_json()
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
    db.save_message(table_name, users_hat.keys(),
                    (update.message.message_id,
                   user.id,
                   update.message.to_json()))
    db.close_connection()
    # print('      √ the message saved to db')
    save_user_to_db(update, context)


def initiate_db():
    print('...' + initiate_db.__name__ + '()')
    db = DbWorker(db_name)
    # db.drop_table(user_data_table)
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
                    experience text,
                    phone_number text)""")

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
    experience = 'NULL' # context.user_data[reply_keyboard[1][0]] \
    # if reply_keyboard[1][0] in context.user_data.keys()
    if 'phone_number'  in update.message.to_dict():
        number = update.message.contact.phone_number
    else:
        number = 'NULL'
    exec_command = f""" INSERT or REPLACE INTO {user_data_table} 
                 VALUES ( {user_id}, '{first_name}', '{last_name}', '{age}', '{gender}', '{experience}', '{number}'
            );"""

    db.exec(exec_command)
    db.close_connection()


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
                MessageHandler(Filters.regex(f'^({reply_keyboard[0][0].text}'
                                             f'|{reply_keyboard[0][1].text})$'),regular_choice),
                MessageHandler(Filters.regex(f'^({reply_keyboard[1][0].text})$'), save_contact),
                MessageHandler(Filters.regex(f'^({reply_keyboard[2][0].text})$'), done)
            ],
            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command |
                                                Filters.regex(f'^({reply_keyboard[2][0].text})$')),
                regular_choice),
                MessageHandler(Filters.regex(f'^({reply_keyboard[2][0].text})$'), done)

            ],
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command |
                                                Filters.regex(f'^({reply_keyboard[2][0].text})$')),
                received_information),
                MessageHandler(Filters.regex(f'^({reply_keyboard[2][0].text})$'), done)

            ],
        },
        fallbacks=[MessageHandler(Filters.regex(f'^(fallbacks)$'), fallbacks)],
    )



    # the handler would handle all metssages that would not handled by others and save to the DB

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
