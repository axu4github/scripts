# coding=utf-8

import os


class Config(object):
    """ 配置 """

    # 根目录地址
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # 日志配置文件名称
    LOG_CONF_FILENAME = "logging_config.ini"
    LOG_CONF_PATH = os.path.join(BASE_DIR, LOG_CONF_FILENAME)

    # 默认 Solr 查询结果文件
    DEFAULT_SOLR_RESULT_FILE = ""

    # Click 模块配置
    CLICK_CONTEXT_SETTINGS = dict(
        help_option_names=["-h", "--help"],
        terminal_width=100)

    SOLR_NODES = ["10.0.3.48:8983", "10.0.3.50:8983"]

    FILE_APPEND = "FILE_APPEND"

    HBASE_HOST = "10.0.3.45"
    HBASE_TABLE = "smartv"
