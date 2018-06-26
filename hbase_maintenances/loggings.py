import logging
from logging.config import fileConfig
from configs import Config


class LoggableMixin(object):

    def __init__(self):
        fileConfig(Config.LOG_CONF_PATH)
        self.logger = logging.getLogger()
