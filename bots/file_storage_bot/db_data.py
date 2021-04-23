from pathlib import Path

db_name = Path('file_storage_bot.py').name[:-3]

messages_table_name = 'main.messages'
user_data_table_name = 'main.user_data'
files_table_name = 'main.fies'

messages_table_format = {
    'message_id': 'integer',
    'user_id': 'integer',
    'is_bot': 'integer',
    'income_time': 'integer',
    'message_text': 'text',
    'message': 'text',
    }

user_data_table_format = {
    'user_id': 'integer not null primary key',
    'first_name': 'integer',
    'last_name': 'string'
    }

files_table_format = {
    'file_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'creation_time': 'integer',
    'file_type': 'text',
    'file_size': 'text',
    'actual_file_name': 'text',
    'tg_file_name': 'text',
    'file_id': 'text',
    'file_unique_id': 'text',
    'mime_type': 'text',
    'duration': 'text',
    'performer': 'text',
    'title': 'text',
    'file': 'blob',
    }


def main() -> None:
    print(db_name)
    # l.info('...' + main.__name__ + '()')
    # initiate_db()
    # updater = Updater(file_storage_1_2_Bot)


if __name__ == '__main__':
    main()
