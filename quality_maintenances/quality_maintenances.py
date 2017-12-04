# -*- coding: utf-8 -*-

import click
import datetime
from quality_tasks import QualityTask
from prettytable import PrettyTable
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

""" 质检任务维护脚本 """

# 头信息
TASK_LIST_HEADERS = ["唯一标识", "质检编号", "质检类型", "质检录音量", "质检开始时间", "日志更新时间"]
TASK_DETAIL_HEADERS = ["执行步骤", "开始执行时间", "耗时"]

DEFAULT_REDIS_HOST = "10.0.3.21"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB_INDEX = 0


def set_if_not_none(judge_value, default_value):
    if judge_value is not None:
        return judge_value
    else:
        return default_value


@click.command()
@click.option("--is_now", default=True, type=click.BOOL, help="是否显示当下的质检任务")
@click.option("--task_id", default=None, help="质检任务 ID")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def main(is_now, task_id, redis_host, redis_port, redis_db):
    """
    质检任务维护脚本

    获取帮助信息请执行 python quality_maintenances.py --help

    例：`python quality_maintenances.py --task_id 20171020_37`

    """
    _redis_host = set_if_not_none(redis_host, DEFAULT_REDIS_HOST)
    _redis_port = set_if_not_none(redis_port, DEFAULT_REDIS_PORT)
    _redis_db = set_if_not_none(redis_db, DEFAULT_REDIS_DB_INDEX)

    table = PrettyTable()
    qt = QualityTask(redis_host=_redis_host,
                     redis_port=_redis_port,
                     redis_db=_redis_db)

    if task_id is not None:
        table.field_names = TASK_DETAIL_HEADERS
        # 样例：task_id => "20170816_397"
        task_id_arr = task_id.split("_")
        task_detail = qt.get_detail(task_id_arr[1], task_id_arr[0])
        total = datetime.timedelta()
        for i in range(0, len(task_detail)):
            (task_step, current_start_time) = task_detail[i]
            (_, previous_start_time) = task_detail[i - 1]
            f_current_start_time = float(current_start_time) / 1000
            f_previous_start_time = float(previous_start_time) / 1000
            interval = "0:00:00.000000"
            if f_current_start_time - f_previous_start_time > 0:
                dt_curr = datetime.datetime.fromtimestamp(f_current_start_time)
                dt_pre = datetime.datetime.fromtimestamp(f_previous_start_time)
                interval = dt_curr - dt_pre
                total += interval  # 计算总耗时

            table.add_row(
                [task_step, qt._format_timestamp(
                    current_start_time), str(interval)]
            )

        print(table)
        print("任务总耗时：[{}].".format(total))
    else:
        table.field_names = TASK_LIST_HEADERS
        for task in qt.get_all(is_now):
            table.add_row([
                task["unique"], task["id"],
                task["type"], task["voicetotal"],
                task["starttime"], task["log_modifiedtime"]])

        print(table)


if __name__ == "__main__":
    main()
