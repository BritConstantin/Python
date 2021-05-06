from pathlib import Path

db_name = Path('file_storage_bot.py').name[:-3]

messages_table_name = 'main.messages'
user_data_table_name = 'main.user_data'
files_table_name = 'main.files'

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
    # 'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    'file_id': 'text',
    'creation_time': 'text',
    'file_type': 'text',
    'file_size': 'text',
    'actual_file_name': 'text',
    'tg_file_name': 'text',
    'file_unique_id': 'text',
    'mime_type': 'text',
    'duration': 'text',
    'performer': 'text',
    'title': 'text',
    'file': 'blob',
    }


def main() -> None:
    print(db_name)



if __name__ == '__main__':
    main()
