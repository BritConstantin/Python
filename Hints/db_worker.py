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
    # TODO: add blob
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
        self.log.info('...DbWorker.' + self.exec.__name__ + '()')
        c = self.conn.cursor()
        try:
            self.log.info("->> trying to execute the command:\n" + command)
            c.execute(command)
            self.conn.commit()
        except sqlite3.OperationalError as e:

            self.log.info('Exception in DbWorker.exec() : ' + str(e))  # self.create_table.__name__ +
        except sqlite3.IntegrityError as e:
            self.log.info('Exception in DbWorker.exec() :' + str(e))  # self.create_table.__name__ +

    def extract_data(self, command):
        self.log.info('...DbWorker.' + self.extract_data.__name__ + '()')

        c = self.conn.cursor()
        try:
            self.log.info("->> trying to execute the command:\n" + command)
            c.execute(command)
            data = c.fetchall()
            return data
        except sqlite3.OperationalError as e:
            self.log.info('Exception in DbWorker.extract_data() :' + str(e))  # self.create_table.__name__ +
        except sqlite3.IntegrityError as e:
            self.log.info('Exception in DbWorker.extract_data() :' + str(e))  # self.create_table.__name__ +

    # done
    def create_table(self, table_name, cols):
        self.log.info('...DbWorker.' + self.create_table.__name__ + '()')

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
            self.log.info('Exception in DbWorker.extract_data() :' + str(e))

    def alter_table(self, table: str,
                    new_col_name: str,
                    new_coll_type: str):
        self.log.info('...DbWorker.' + self.alter_table.__name__ + '()')

        c = self.conn.cursor()
        try:
            command = f"""ALTER TABLE {table}
                      ADD COLUMN {new_col_name} {new_coll_type};"""
            c.execute(command)
            self.conn.commit()
        except sqlite3.OperationalError as e:
            self.log.info('Exception in DbWorker.alter_table() :' + str(e))

    def drop_table(self, table_name):
        self.log.info('...DbWorker.' + self.drop_table.__name__ + '()')

        c = self.conn.cursor()
        sql_command = f"DROP TABLE {table_name}"
        c.execute(sql_command)

    # done
    def print_table(self, table_name):
        self.log.info('...DbWorker.' + self.print_table.__name__ + '()')

        c = self.conn.cursor()

        try:
            with self.conn:
                c.execute(f"SELECT * FROM {table_name}")
            for s in c.fetchall():
                print(s)
        except sqlite3.OperationalError as e:
            self.log.info(f'...DbWorker.{self.print_table.__name__}() raised sqlite3.OperationalError: \n{e}')
        except Exception as e:
            self.log.info(f'...DbWorker.{self.print_table.__name__}() raised exception: \n{e}')

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
            self.log.info(f'...DbWorker.{self.get_all_table_rows.__name__}() raised sqlite3.OperationalError: \n{e}')

    def save_message(self, table_name: str, row: list) -> None:
        self.log.info('...DbWorker.' + self.save_message.__name__ + '()')

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
            self.log.info(f'...DbWorker.{self.save_message.__name__}() raised sqlite3.OperationalError: \n{e}')

    # TODO: !1 WIP Finish implementation
    #
    def save_tg_file(self, table_name: str, row: dict) -> None:
        self.log.info('...DbWorker.' + self.get_all_table_rows.__name__ + '()')
        self.log.debug(f'\n\tincome args\n\ttable_name={type(table_name)},\n\trow{type(row)}')
        self.log.debug(f'\n row is: {row}\n')
        c = self.conn.cursor()
        values = ""
        sql_commnand = ""
        try:
            for r in row.values():
                print(f' type of income field={type(r)}')
                if type(r) == "<class 'datetime.datetime'>":  #
                    r = str(r)
                    r = r.replace("'", "''")
                    values += f'"{r}" , '
                elif  type(r) != "<class 'bytes'>":
                    values+= f'"{r}", '
                    print(f'Date time is look like:{r}')
                else:
                    values += f'{r}, '
            sql_commnand = f" INSERT INTO {table_name} VALUES ({values[:-2]}) "
            self.log.info(sql_commnand)
            c.execute(sql_commnand)
            self.conn.commit()

        except sqlite3.OperationalError as e:
            self.log.info(f'...DbWorker.{self.save_tg_file.__name__}() raised sqlite3.OperationalError: \n{e}')
        except Exception as e:
            self.log.info(f'...DbWorker.{self.save_tg_file.__name__}() raised exception: \n{e}')

    def close_connection(self):
        self.conn.close()  # close the connection to the DB
