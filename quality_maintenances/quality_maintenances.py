# -*- coding: utf-8 -*-

import re
import time
import click
import datetime
import pymysql
from quality_tasks import QualityTask
from prettytable import PrettyTable
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

""" 质检任务维护脚本 """

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# click 模块配置
CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    terminal_width=100)
CLICK_COLOR_INFO = "green"
CLICK_COLOR_ERROR = "red"

# 头信息
TASK_LIST_HEADERS_NAME = ["唯一标识", "质检编号", "质检类型", "质检录音量", "规则数量", "关键词数量",
                          "质检任务状态", "质检开始时间", "日志更新时间", "耗时", "执行服务器"]
TASK_LIST_HEADERS_CODE = ["unique", "id", "type", "voicetotal",
                          "rule_num", "kw_num",
                          "status", "starttime", "log_modifiedtime",
                          "interval", "nodename"]
TASK_DETAIL_HEADERS = ["执行步骤", "开始执行时间", "耗时"]

# 质检类型
QUALITY_TASK_TYPE = {
    "A": "常规质检(A)",
    "B": "专项质检(B)",
    "C": "关联质检(C)",
    "D": "常规关联质检(D)",
}

# 质检任务状态
QUALITY_TASK_STATUS = {
    "A": "未启动(A)",  # CREATE
    "B": "已取消(B)",  # CANCEL
    "C": "启动(C)",  # STARTUP
    "D": "执行中(D)",  # RUNNING
    "E": "已完成(E)",  # DONE
    "F": "失败(F)",  # FAILURE
    "I": "预处理(I)",  # YCL
    "W": "排队中(W)"  # DDZ
}

DEFAULT_REDIS_HOST = "10.0.3.21"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB_INDEX = 0

MYSQL_HOST = "10.0.1.68"
MYSQL_USER = "root"
MYSQL_PASSWD = "root123"
MYSQL_DB = "quality"

SQL = """
    SELECT
        qrd.detectionExpression
    FROM
        QualityRuleDetection qrd,
        QualityTask qt,
        QualityRule qr
    WHERE
        qt.qualityRuleId = qr.id AND
        qrd.qualityId = qr.id AND
        qt.id = {0};
"""

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                       passwd=MYSQL_PASSWD, db=MYSQL_DB)
cur = conn.cursor()


def get_detail_by(task_id):
    """ 根据质检任务编号获取该任务的 关键词数量 和 规则数量 """
    rule_num = cur.execute(SQL.format(task_id))
    kw_str = "and".join([rule[0] for rule in cur]).lower()
    kw_num = len(re.split(r"and|or|near|after|before|,", kw_str))

    return (rule_num, kw_num)


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


def tasks_filter(tasks, tail, date_filter, status_filter,
                 type_filter, server_filter, s="|"):
    """ 任务过滤方法，通过不同条件过滤质检任务列表。 """

    # 通过日期过滤
    if date_filter is not None:
        tasks = filter(lambda t: t["unique"].startswith(date_filter), tasks)

    # 通过状态过滤
    if status_filter is not None:
        tasks = filter(
            lambda t: t["status"].upper() in status_filter.upper().split(s),
            tasks)

    # 通过质检类型过滤
    if type_filter is not None:
        tasks = filter(
            lambda t: t["type"].upper() in type_filter.upper().split(s),
            tasks)

    # 通过服务器名称过滤
    if server_filter is not None:
        tasks = filter(
            lambda t: t["nodename"].upper() in server_filter.upper().split(s),
            tasks)

    # 通过条数过滤
    if tail > 0:
        tasks = tasks[-1 * tail:]

    return tasks


def tasks_formater(tasks, show_detail):
    """ 将质检任务信息转换为输出内容 """
    def formater(task):
        start_datetime = datetime.datetime.strptime(
            task["starttime"], "%Y-%m-%d %H:%M:%S")
        interval = datetime.timedelta()
        if task["endtime"] != 0 and task["status"].upper() == "E":
            end_datetime = datetime.datetime.strptime(
                task["endtime"], "%Y-%m-%d %H:%M:%S")
            interval = end_datetime - start_datetime

        task["interval"] = interval

        del(task["endtime"])
        del(task["createtime"])

        if show_detail:
            (rule_num, kw_num) = get_detail_by(task["id"])
            task["rule_num"] = rule_num
            task["kw_num"] = kw_num
        else:
            task["rule_num"] = "-"
            task["kw_num"] = "-"

    map(formater, tasks)
    return tasks


def get_export_file(export_file=None):
    """ 获取导出文件地址 """
    if export_file is None:
        export_file = "{0}/exported_{1}.csv".format(BASE_DIR, time.time())

    return export_file


def csvfile_put_contents(file, contents):
    """ 写CSV文件 """
    import csv
    with open(file, "w") as csvfile:
        fieldnames = TASK_LIST_HEADERS_CODE
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contents)


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
@click.option("--tail", default=0, type=click.INT, help="最后n条记录")
@click.option("--date_filter", default=None, help="根据时间过滤质检任务信息")
@click.option("--status_filter", default=None, help="根据状态过滤质检任务信息")
@click.option("--type_filter", default=None, help="根据质检任务类型过滤质检任务信息")
@click.option("--server_filter", default=None, help="根据服务器名称过滤质检任务信息")
@click.option("--show_detail", default=False, type=click.BOOL, help="是否显示详细信息")
@click.option("--export_result", default=False, type=click.BOOL, help="是否导出文件")
@click.option("--export_file", default=None, help="自定义导出文件")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def list(is_now, tail, show_detail, export_result, export_file,
         date_filter, status_filter, type_filter, server_filter,
         redis_host, redis_port, redis_db):
    """
    显示质检任务列表信息

    ## 实例：

    - 获取正在处理的质检任务信息: `python quality_maintenances.py list`

    - 获取已经处理完成的质检任务信息: `python quality_maintenances.py list --is_now=false`

    ## 修改日志（Change Log）

    ### 2018-01-02

    - 添加 date_filter 参数，以便完成 根据时间过滤质检任务信息 需求。

    - 添加 status_filter 参数，以便完成 根据状态过滤质检任务信息 需求。

    - 添加 type_filter 参数，以便完成 根据质检任务类型过滤质检任务信息 需求。

    - 添加 server_filter 参数，以便完成 根据服务器名称过滤质检任务信息 需求。

    - 添加 show_detail 参数，以便完成 在列表命令时显示更多的信息 需求。
      增加显示项 关键词数量、规则数量、整体执行时间、任务执行状态；并为之后的导出功能提供数据基础。

    - 添加 export_result 参数，以便完成 导出列表命令显示结果 需求。

    - 添加 export_file 参数，以便完成 导出自定义指定导出文件 需求。
    """
    qt = _init_quality_task(redis_host, redis_port, redis_db)
    tasks = qt.get_all(is_now)
    # 过滤
    tasks = tasks_filter(tasks, tail, date_filter,
                         status_filter, type_filter, server_filter)
    # 转换
    tasks = tasks_formater(tasks, show_detail)
    if not export_result:
        table = PrettyTable()
        table.field_names = TASK_LIST_HEADERS_NAME
        for task in tasks:
            row = [task["unique"],
                   task["id"],
                   QUALITY_TASK_TYPE[task["type"].upper()],
                   task["voicetotal"],
                   task["rule_num"],
                   task["kw_num"],
                   QUALITY_TASK_STATUS[task["status"].upper()],
                   task["starttime"],
                   task["log_modifiedtime"],
                   task["interval"],
                   task["nodename"]]
            table.add_row(row)

        click.echo()
        click.echo(table)
    else:
        if len(tasks) > 0:
            file = get_export_file(export_file)
            csvfile_put_contents(file, tasks)
            click.echo(
                click.style("导出完成：{0}".format(file), fg=CLICK_COLOR_INFO))
        else:
            click.echo(click.style("没有内容！", fg=CLICK_COLOR_ERROR))


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
    qt = _init_quality_task(redis_host, redis_port, redis_db)
    table = PrettyTable()
    table.field_names = TASK_DETAIL_HEADERS
    # 样例：task_id => "20170816_397"
    task_id_arr = task_id.split("_")
    task_details = qt.get_detail(task_id_arr[1], task_id_arr[0])
    total = 0
    for task_detail in task_details:
        (task_step, start_time, interval) = task_detail
        total += interval  # 单位：毫秒

        table.add_row(
            [task_step, qt._format_timestamp(start_time),
             datetime.timedelta(milliseconds=interval)]
        )

    click.echo(table)
    # 兼容 python2.6 由 "{}" 改为 "{0}"
    click.echo("质检任务总耗时：{0}".format(
        click.style(
            str(datetime.timedelta(milliseconds=total)), fg=CLICK_COLOR_INFO)))


@cli.command(short_help="显示质检任务运行日志")
@click.option("--task_id", required=True, help="质检任务 ID")
@click.option("--number", "-n", default=0, type=click.INT, help="显示最后N条记录")
@click.option("--redis_host", default=None, help="Redis 服务 IP 地址")
@click.option("--redis_port", default=None, type=click.INT, help="Redis 服务端口号")
@click.option("--redis_db", default=None, type=click.INT, help="Redis DB 索引")
def log(task_id, number, redis_host, redis_port, redis_db):
    """
    显示质检任务运行日志

    实例：`python quality_maintenances.py log --task_id=20171020_37`
    """
    # 样例：task_id => "20170816_397"
    task_unique = task_id.split("_")[1]
    qt = _init_quality_task(redis_host, redis_port, redis_db)
    log_paths = qt._get_log_path(task_unique)
    if len(log_paths) > 0:
        log_path = log_paths[0]
        # 兼容 python2.6 由 "{}" 改为 "{n}"
        if number > 0:
            cmd = "tail -n {0} {1}".format(number, log_path)
        else:
            cmd = "tail -f {0}".format(log_path)

        click.echo(click.style("执行命令：{0}".format(cmd), fg=CLICK_COLOR_INFO))
        os.system(cmd)
        click.echo(os.linesep)
    else:
        click.echo(click.style("错误：没有找到对应的日志文件！", fg=CLICK_COLOR_ERROR))


if __name__ == "__main__":
    cli()
