from random import randint

from Hints.db_worker import DbWorker
from assignments.conversationbot_3_0 import db_name as conv30_dbname
from bots.file_storage_bot.db_data import files_table_name, db_name, files_table_format


def work1():
    db_name = "../assignments/users2"
    conv30_dbname_l = "../assignments/" + conv30_dbname
    table_name = 'users'
    user_data_table_name = 'user_data'
    user_data_cols = [
        [('user_id'), ('integer not null primary key')],
        [('first_name'), ('text')],
        [('last_name'), ('text')],
        [('age'), ('text')],
        [('gender'), ('text')],
        [('experience'), ('text')],
        [('phone_number'), ('text')]]

    users_hat = {
        'message_id': 'integer',
        'user_id': 'integer',
        'message': 'string'
        }
    test_row = (randint(1, 1000), "stub_name" + str(randint(1, 1000)), "stub message" + str(randint(1, 1000)))
    db = DbWorker(conv30_dbname)
    db.alter_table(user_data_table_name, user_data_cols[-1][0], user_data_cols[-1][1])
    extracted_data = db.get_all_table_rows(user_data_table_name)
    print("ed> ")
    for s in extracted_data:
        print(s)
    db.close_connection()


def delete_file_table():
    relative_path = f"../bots/file_storage_bot/{db_name}"
    db = DbWorker(relative_path)
    db.get_all_table_rows(files_table_name)
    db.drop_table(files_table_name)
    db.close_connection()


def create_new_file_table():
    relative_path = f"../bots/file_storage_bot/{db_name}"
    db = DbWorker(relative_path)
    db.create_table(files_table_name,files_table_format)
    db.get_all_table_rows(files_table_name)
    db.close_connection()


if __name__ == '__main__':
    # delete_file_table()
    create_new_file_table()
    # work1()
