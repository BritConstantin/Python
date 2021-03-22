from random import randint

from Hints.db_worker import DbWorker
from assignments.conversationbot_3_0 import db_name as conv30_dbname

if __name__ == '__main__':
    db_name = "../assignments/users2"
    conv30_dbname = "../assignments/" + conv30_dbname
    table_name = 'users'
    user_data_table_name = 'user_data'
    user_data_cols = [
        [('user_id'),('integer not null primary key')],
        [('first_name'), ('text')],
        [('last_name'), ('text')],
        [('age'),( 'text')],
        [('gender'),('text')],
        [('experience'),('text')],
        [('phone_number'),('text')]]

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
