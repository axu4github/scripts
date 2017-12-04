# -*- coding: utf-8 -*-

import click
import datetime
from quality_tasks import QualityTask
from prettytable import PrettyTable
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

""" 质检任务维护脚本 """

# click 模块配置
CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    terminal_width=100)
CLICK_COLOR = "red"
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


def _init_quality_task(redis_host, redis_port, redis_db):
    """ 初始化 QualityTask 实例 """
    _host = set_if_not_none(redis_host, DEFAULT_REDIS_HOST)
    _port = set_if_not_none(redis_port, DEFAULT_REDIS_PORT)
    _db = set_if_not_none(redis_db, DEFAULT_REDIS_DB_INDEX)
    return QualityTask(redis_host=_host, redis_port=_port, redis_db=_db)


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.help_option("-h", "--help", help="使用说明")
def cli():
    """
    质检任务运维脚本

    获取帮助信息请执行 python quality_maintenances.py --help
    """
    pass


@cli.command(short_help="显示质检任务列表信息")
@click.help_option("-h", "--help", help="使用说明")
@click.option("--is_now", default=True, type=click.BOOL, help="是否显示当下的质检任务")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def list(is_now, redis_host, redis_port, redis_db):
    """
    显示质检任务列表信息

    实例：

    - 获取正在处理的质检任务信息: `python quality_maintenances.py list`

    - 获取已经处理完成的质检任务信息: `python quality_maintenances.py list --is_now=false`
    """
    table = PrettyTable()
    qt = _init_quality_task(redis_host, redis_port, redis_db)
    table.field_names = TASK_LIST_HEADERS
    for task in qt.get_all(is_now):
        table.add_row([
            task["unique"], task["id"],
            task["type"], task["voicetotal"],
            task["starttime"], task["log_modifiedtime"]])

    click.echo()
    click.echo(table)


@cli.command(short_help="显示质检任务详细信息")
@click.help_option("-h", "--help", help="使用说明")
@click.option("--task_id", required=True, help="质检任务 ID")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def detail(task_id, redis_host, redis_port, redis_db):
    """
    显示质检任务详细信息

    实例：`python quality_maintenances.py detail --task_id=20171020_37`
    """
    table = PrettyTable()
    qt = _init_quality_task(redis_host, redis_port, redis_db)
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

    click.echo(table)
    click.echo("质检任务总耗时 => {}".format(click.style(str(total), fg=CLICK_COLOR)))


if __name__ == "__main__":
    cli()
