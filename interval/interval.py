# -*- coding: utf-8 -*-

import click
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

""" 计算间隔时间 """

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def str2datetime(date, date_format=DATE_FORMAT):
    """ 字符串时间 转换为 datetime """
    return datetime.datetime.strptime(date, date_format)


@click.command()
@click.argument("start")
@click.argument("end")
@click.option("--date_format", default=DATE_FORMAT,
              help="日期格式，默认为：%Y-%m-%d %H:%M:%S")
def interval(start, end, date_format):
    start = str2datetime(start, date_format)
    end = str2datetime(end, date_format)
    if start > end:
        start, end = end, start

    print(end - start)


if __name__ == "__main__":
    interval()
