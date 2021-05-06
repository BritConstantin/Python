from random import randint

from Hints.db_worker import DbWorker
from assignments.conversationbot_3_0 import db_name as conv30_dbname
from bots.file_storage_bot.db_data import files_table_name, db_name, files_table_format


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
    delete_file_table()
    create_new_file_table()