from pathlib import Path

import yaml


class ConfigFileNotFoundException(Exception):
    def __init__(self):
        self.message = 'config.yaml is not present in the project root'
        super().__init__(self.message)


class _MailConfiguration:
    def __init__(self, mail_conf: dict):
        self.__mail = mail_conf

        self.NAME = self.__mail.get('NAME')
        self.ADDRESS = self.__mail.get('ADDRESS')
        self.HOST = self.__mail.get('HOST')
        self.USE_TLS = self.__mail.get('USE_TLS')
        self.PORT = self.__mail.get('PORT')
        self.REPLY_TO = self.__mail.get('REPLY_TO')


class _DBConfiguration:
    def __init__(self, db_conf: dict):
        self.__db = db_conf

        self.ENGINE = self.__db.get('NAME')
        self.NAME = self.__db.get('ADDRESS')
        self.HOST = self.__db.get('HOST')
        self.PORT = self.__db.get('PORT')


class Configuration:

    def __init__(self, path: Path):
        self.__path = path
        self.__config = self.__load_yaml()

        self.PROJECT_NAME = self.__config.get('NAME')
        self.MAIL = _MailConfiguration(self.__config.get('MAIL'))
        self.DB = _DBConfiguration(self.__config.get('DB'))
        self.ALLOWED_HOST = self.__config.get('ALLOWED_HOST')
        self.CORS_ALLOWED_ORIGIN = self.__config.get('CORS_ALLOWED_ORIGIN')

    def __load_yaml(self):
        if self.__path.exists():
            with open(self.__path) as yaml_file:
                return yaml.load(yaml_file, Loader=yaml.FullLoader)
        else:
            raise ConfigFileNotFoundException
