import logging


class TgFileWorker:

    def __init__(self, db_name, loglevel=logging.INFO):
        logging.basicConfig()
        self.actual_file_name = ""
        logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', level=logging.INFO)
        self.log = logging.getLogger(__name__)
        self.log.level = loglevel
