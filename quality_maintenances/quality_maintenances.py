# -*- coding: utf-8 -*-

import click
from quality_tasks import QualityTask
from prettytable import PrettyTable
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

""" 质检任务维护脚本 """

# 头信息
HEADERS = ["唯一标识", "质检编号", "质检类型", "质检录音量", "质检开始时间", "日志更新时间"]
DEFAULT_REDIS_HOST = "172.31.117.31"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB_INDEX = 0


def set_if_not_none(judge_value, default_value):
    if judge_value is not None:
        return judge_value
    else:
        return default_value


@click.command()
@click.option("--is_now", default=True, type=click.BOOL, help="是否显示当下的质检任务")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def main(is_now, redis_host, redis_port, redis_db):
    """
    质检任务维护脚本

    获取帮助信息请执行 python quality_maintenances.py --help
    """
    _redis_host = set_if_not_none(redis_host, DEFAULT_REDIS_HOST)
    _redis_port = set_if_not_none(redis_port, DEFAULT_REDIS_PORT)
    _redis_db = set_if_not_none(redis_db, DEFAULT_REDIS_DB_INDEX)

    table = PrettyTable()
    table.field_names = HEADERS
    qt = QualityTask(redis_host=_redis_host,
                     redis_port=_redis_port,
                     redis_db=_redis_db)

    for task in qt.get_all(is_now):
        table.add_row([
            task["unique"], task["id"],
            task["type"], task["voicetotal"],
            task["starttime"], task["log_modifiedtime"]])

    print table


if __name__ == "__main__":
    main()
