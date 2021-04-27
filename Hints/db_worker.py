import logging
import sqlite3
from random import randint

"""
SqLite supported data types:
    NULL
    TEXT - string
    INTEGER
    REAL - float
    BLOB - any type file
"""


class DbWorker:
    # todo: Add log level to class
    # todo: add normal exception handling to all methods(logger)

    def __init__(self, db_name, loglevel=logging.INFO):
        logging.basicConfig()
        self.conn = sqlite3.connect(f'{db_name}.db')
        self.db_name = db_name
        logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.level = loglevel

    def exec(self, command):
        c = self.conn.cursor()
        try:
            self.log.info("->> trying to execute the command:\n" + command)
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
            self.log.info("->> trying to execute the command:\n" + command)
            c.execute(command)
            data = c.fetchall()
            return data
        except sqlite3.OperationalError as e:
            print('Exception in DbWorker.extract_data() :')
            print('`' + str(e))  # self.create_table.__name__ +
        except sqlite3.IntegrityError as e:
            print('Exception in DbWorker.extract_data() :')
            print('`' + str(e))  # self.create_table.__name__ +

    # done
    def create_table(self, table_name, cols):
        c = self.conn.cursor()
        cols_str = ""
        try:
            for col_name in cols.keys():
                cols_str += col_name + " " + cols[col_name] + ", "
            cols_str = cols_str[:-2]
            sql_command = f"""CREATE TABLE IF NOT EXISTS {table_name} ( {cols_str} )"""
            self.log.debug(' executing: ' + sql_command)
            c.execute(sql_command)


        except sqlite3.OperationalError as e:
            print(e)  # self.create_table.__name__ +

    def alter_table(self, table: str,
                    new_col_name: str,
                    new_coll_type: str):
        c = self.conn.cursor()
        try:
            command = f"""ALTER TABLE {table}
                      ADD COLUMN {new_col_name} {new_coll_type};"""
            c.execute(command)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(self.create_table.__name__)
            print(e)

    # def drop_table(self, table_name):
    #     c = self.conn.cursor()
    #     sql_command = f"DROP TABLE {table_name}"
    #     # print(' executing: ' + sql_command)
    #     c.execute(sql_command)

    # done
    def print_table(self, table_name):
        c = self.conn.cursor()

        try:
            with self.conn:
                c.execute(f"SELECT * FROM {table_name}")
            for s in c.fetchall():
                print(s)
        except sqlite3.OperationalError as e:
            print("ERROR in " + self.create_table.__name__)
            print(e)

    def get_all_table_rows(self, table_name):
        self.log.info('...' + self.get_all_table_rows.__name__ + '()')
        c = self.conn.cursor()

        try:
            with self.conn:
                c.execute(f"SELECT * FROM {table_name}")
                tmp = c.fetchall()
                self.log.info(tmp)
                return tmp

        except sqlite3.OperationalError as e:
            print("ERROR in " + self.create_table.__name__)
            print(e)

    def save_message(self, table_name: str, row: list) -> None:
        c = self.conn.cursor()
        try:
            for r in range(len(row)):
                l = list(row)
                if str(type(l[r])) == "<class 'str'>" and "'" in l[r]:
                    l[r] = str(l[r]).replace("'", "''")

            c.execute(f"""
               INSERT INTO {table_name}
               VALUES ({l[0]},'{l[1]}','{l[2]}')
                           """)
            # c.execute(f"""INSERT INTO {table_name}
            #               VALUES ({str(column_names[0])}, {column_names[1]}, {column_names[2]}) """)
            self.conn.commit()

        except sqlite3.OperationalError as e:
            print(self.save_message.__name__)
            print(e)  # self.create_table.__name__ +
    # TODO: !1 WIP Finish implementation
    def save_tg_file(self, table_name: str, row: dict) -> None:
        c = self.conn.cursor()
        values = ""
        sql_commnand = ""
        print(row)
        try:
            for r in row.values():
                if type(r) == "<class 'str'>" and "'" in r:
                   r = r.replace("'", "''")
                print(f'___{r}')
                values +=f"'{r}', "
            sql_commnand =f" INSERT INTO {table_name} VALUES ({values}) "
            print(sql_commnand)
            c.execute(sql_commnand)
            self.conn.commit()

        except sqlite3.OperationalError as e:
            print(self.save_message.__name__)
            print(e)  # self.create_table.__name__ +

    def close_connection(self):
        self.conn.close()  # close the connection to the DB
