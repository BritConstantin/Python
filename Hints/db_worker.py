import sqlite3
from random import randint

"""
SqLite supported method:
    TEXT
    NUMERIC
    INTEGER
    REAL
    BLOB
"""


class DbWorker:
    # todo: Add log level to class

    def __init__(self, db_name):
        self.conn = sqlite3.connect(f'{db_name}.db')
        self.db_name = db_name

    def exec(self, command):
        c = self.conn.cursor()
        try:
            c.execute(command)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print('Exception in DbWorker.exec() :')
            print('`' + str(e))  # self.create_table.__name__ +
        except sqlite3.IntegrityError as e:
            print('Exception in DbWorker.exec() :')
            print('`' + str(e))  # self.create_table.__name__ +

    def extract_data(self, command):
        c = self.conn.cursor()
        try:
            c.execute(command)
            data = c.fetchall()
            return data
        except sqlite3.OperationalError as e:
            print('Exception in DbWorker.exec() :')
            print('`' + str(e))  # self.create_table.__name__ +
        except sqlite3.IntegrityError as e:
            print('Exception in DbWorker.exec() :')
            print('`' + str(e))  # self.create_table.__name__ +

    # done
    def create_table(self, table_name, cols):
        c = self.conn.cursor()
        cols_str = ""
        try:
            for col_name in cols.keys():
                cols_str += col_name + " " + cols[col_name] + ", "
            cols_str = cols_str[:-2]
            sql_command = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                        {cols_str}
                        )"""
            # print(' executing: ' + sql_command)
            c.execute(sql_command)


        except sqlite3.OperationalError as e:
            print(e)  # self.create_table.__name__ +

    def alter_table(self, table: str,
                    new_col_name: str,
                    new_coll_type: str):
        c = self.conn.cursor()
        command = f"""ALTER TABLE{table}
                      ADD COLUMN {new_col_name} {new_coll_type};"""
        c.execute(command)
        self.conn.commit()
        self.close_connection()

    def drop_table(self, table_name):
        c = self.conn.cursor()
        sql_command = f"DROP TABLE {table_name}"
        # print(' executing: ' + sql_command)
        c.execute(sql_command)

    # done
    def print_table(self, table_name):
        c = self.conn.cursor()

        try:
            with self.conn:
                c.execute(f"SELECT * FROM {table_name}")
            for s in c.fetchall():
                print(s)
        except sqlite3.OperationalError as e:
            print(self.create_table.__name__)
            print(e)

    def get_all_table_rows(self, table_name):

        print('...' + self.get_all_table_rows.__name__ + '()')
        c = self.conn.cursor()

        try:
            with self.conn:
                c.execute(f"SELECT * FROM {table_name}")
                tmp = c.fetchall()
                print(tmp)
                return tmp

        except sqlite3.OperationalError as e:
            print(self.create_table.__name__)
            print(e)

    def insert_row(self, table_name, column_names, row):
        c = self.conn.cursor()
        try:
            # c.execute(f"""
            # INSERT INTO users
            # VALUES (1,'test_name','test_message')
            #             """)
            c.execute(f"""
               INSERT INTO {table_name}
               VALUES ({row[0]},'{row[1]}','{row[2]}')
                           """)
            # c.execute(f"""INSERT INTO {table_name}
            #               VALUES ({str(column_names[0])}, {column_names[1]}, {column_names[2]}) """)
            self.conn.commit()

        except sqlite3.OperationalError as e:
            print(e)  # self.create_table.__name__ +

    def close_connection(self):
        self.conn.close()  # close the connection to the DB


if __name__ == '__main__':
    db_name = "users2"
    table_name = 'users'
    user_data_table_name = 'user_data'
    user_data_cols = {
        'user_id': 'integer not null primary key',
        'first_name': 'text',
        'last_name': 'text',
        'age': 'text',
        'gender': 'text',
        'experience': 'text',
        'phone_number':'text'
    }
    users_hat = {
        'message_id': 'integer',
        'user_id': 'integer',
        'message': 'string'
    }
    test_row = (randint(1, 1000), "stub_name" + str(randint(1, 1000)), "stub message" + str(randint(1, 1000)))
    db = DbWorker(db_name)

    # my_db.drop_table(db_name)
    # my_db.create_table(table_name, users_hat)
    # my_db.print_table(table_name)
    # print('----------------------')
    # my_db.insert_row(table_name, users_hat.keys(), test_row)
    # my_db.print_table(table_name)
    # db.alter(table_name, user_data_cols.keys()[-2], user_data_cols.values()[-2])
    # db.alter_table(table_name, user_data_cols['experience'], user_data_cols.values()[-1])
    extracted_data = db.get_all_table_rows(table_name)
    print("ed> ")
    for s in extracted_data:
        print(s)

    db.close_connection()
