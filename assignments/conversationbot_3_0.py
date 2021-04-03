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
# done: check how to get user number
# done: add check 'is_all_datat_filled?'
# done: save phone_number in to DB
# todo: add selection of genger like mail|female
# todo: add check 'can_i_use_your_photo?'
# todo: study how to use logger correct
#          logger.info(
#         "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
#     )
# todo: learn how to work with pickling
# todo: add ability to edit entered  data
# region Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion

# region Global variables declaration
# DB vars
db_name = Path(__file__).name[:-3]
user_data_table = 'main.user_data'
messages_table_name = 'main.messages'
user_data_table_format = {
    'message_id': 'integer',
    'user_id': 'integer',
    'message': 'string'
    }
# Conversation stages
CHOOSING, TYPING_REPLY, TYPING_CHOICE, REGISTERED = range(4)
# Creating of keyboard markup
reply_keyboard = [
    [KeyboardButton('Age'), KeyboardButton('Gender')],
    [KeyboardButton('Number', request_contact=True)],
    [KeyboardButton('Done')]
    ]
markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, one_time_keyboard=True, )


# endregion


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} : {value}')

    return "\n".join(facts).join(['\n', '\n'])


# region     Handlers
def start(update: Update, context: CallbackContext) -> int:
    print('...' + start.__name__ + '()')
    save_message_to_db(update, context)

    reply = update.message.reply_text(
            "Hi! I'm conversation bot 3 0 \n"
            "If you want to start new chat please fill the form:\nAge:\nGender:\nNumber:",
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

    reply = update.message.reply_text(f'Your {text.lower()}?')
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)

    is_registration_done(update, context)
    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    print('...' + received_information.__name__ + '()')
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']
    # print(context.user_data)
    save_message_to_db(update, context)
    reply = update.message.reply_text(
            "Neat! Just so you know, this is what you already fill:"
            f"{facts_to_str(user_data)}",
            reply_markup=markup,
            )
    bot_update = Update(update_id=update.update_id + 1, message=reply)
    save_message_to_db(bot_update, context)
    is_registration_done(update, context)
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


def is_registration_done(update: Update, context: CallbackContext):
    print('...' + is_registration_done.__name__ + '()')
    counter = 0
    if reply_keyboard[0][0].text in context.user_data.keys():
        print(f'     √ {reply_keyboard[0][0].text} -> {context.user_data[reply_keyboard[0][0].text]}')
        counter += 1
    if reply_keyboard[0][1].text in context.user_data:
        print(f'     √ {reply_keyboard[0][1].text} -> {context.user_data[reply_keyboard[0][1].text]}')
        counter += 1
    if "phone_number" in context.user_data:
        print(f'     √ {"phone_number"} -> {context.user_data["phone_number"]}')
        counter += 1

    if counter == 3:
        update.message.from_user.send_message("Thanks you for your registration")

        # return REGISTERED
        return ConversationHandler.END
    else:
        update.message.from_user.send_message("Please continue registration")
        return CHOOSING


def save_contact(update: Update, context: CallbackContext):
    print('...' + save_contact.__name__ + '()')

    save_message_to_db(update, context)
    if 'phone_number' in update.message.to_json():
        context.user_data['phone_number'] = update.message.contact.phone_number
        reply = update.message.from_user.send_message(
                "Neat! Just so you know, this is what you already fill:"
                f"{facts_to_str(context.user_data)}"
                )
        bot_update = Update(update_id=update.update_id + 1, message=reply)
        save_message_to_db(bot_update, context)

    is_registration_done(update, context)
    return CHOOSING


# endregion

# region DB methods
def save_message_to_db(update: Update, context: CallbackContext):
    print('...' + save_message_to_db.__name__ + '()', end='->')
    user = update.message.from_user
    if 'text' in update.message.to_dict():
        t = update.message.text
        text = t if len(t) <= 25 else t[:25]
    else:
        text = update.message.to_json()
    print(f' {update.message.message_id} '
          f'user {user.full_name}({user.id}):"' + text + '"')

    db = DbWorker(db_name)

    db.create_table(messages_table_name, user_data_table_format)
    db.save_message(messages_table_name,
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
    print('...' + save_user_to_db.__name__ + '() ->', end=' ')
    db = DbWorker(db_name)
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    try:
        age = context.user_data[reply_keyboard[0][0].text] if reply_keyboard[0][
                                                                  1].text in context.user_data.keys() else 'NULL'
        gender = context.user_data[reply_keyboard[0][1].text] \
            if reply_keyboard[0][1].text in context.user_data.keys() else 'NULL'
        experience = 'NULL'  # context.user_data[reply_keyboard[1][0]] \
        # if reply_keyboard[1][0] in context.user_data.keys()
        if 'contact' in update.message.to_json():
            if 'phone_number' in update.message.contact.to_json():
                number = update.message.contact.phone_number
                # print(f'--------if------> phone number is in. Saving it to db{update.message.contact.phone_number}')
        elif 'phone_number' in context.user_data:
            number = context.user_data['phone_number']
            # print(f'--------elif------> phone number is in. Saving it to db{context.user_data}')
        else:
            number = 'NULL'
        exec_command = f""" INSERT or REPLACE INTO {user_data_table} 
                     VALUES ( {user_id}, '{first_name}', '{last_name}', '{age}', '{gender}', '{experience}', '{number}'
                );"""
        print(f'{age}, {gender},{experience}, {number}')
        db.exec(exec_command)
        db.close_connection()
    except Exception as e:
        print(f"""          EXception handled in {db_name}{save_user_to_db.__name__}, exeption is: 
                {e}""")


# endregion


def stop(update: Update, context: CallbackContext):
    print('...' + stop.__name__ + '() ->', end=' ')
    save_message_to_db(update, context)
    ConversationHandler.END

def timeout(conversations):
    print('...' + timeout.__name__ + '() ->', end=' ')
    # save_message_to_db(update, context)
    for s in conversations:
        print(f'        {s}')
    ConversationHandler.END


def susers_online(update: Update, context: CallbackContext):
    update.message.from_user.send_message("For now you are the one online.")



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
                                                 f'|{reply_keyboard[0][1].text})$'), regular_choice),
                    MessageHandler(Filters.contact, save_contact),
                    MessageHandler(Filters.regex(f'^({reply_keyboard[2][0].text})$'), done)
                    ],
                TYPING_REPLY: [
                    MessageHandler(Filters.text & ~(Filters.command |
                                                    Filters.regex(f'^({reply_keyboard[2][0].text})$')),
                                   received_information),
                    MessageHandler(Filters.regex(f'^({reply_keyboard[2][0].text})$'), done)

                    ],
                REGISTERED: [
                    MessageHandler(Filters.command('users_online'), susers_online)
                    ]
                },
            fallbacks=[CommandHandler('stop',stop )],
            # conversation_timeout=10,

            )
    # conv_handler._trigger_timeout(context= job=timeout(conv_handler.conversations))
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(Filters.text , save_message_to_db))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
