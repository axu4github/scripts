# -*- coding: utf-8 -*-

from quality_tasks import QualityTask
from prettytable import PrettyTable

""" 质检任务维护脚本 """

# 头信息
HEADERS = ["唯一标识", "质检编号", "质检类型", "质检录音量", "质检开始时间", "日志更新时间"]


def main():
    row = PrettyTable()
    row.field_names = HEADERS
    qt = QualityTask(redis_host="172.31.117.31")
    for task in qt.get_all(False):
        row.add_row([
            task["unique"], task["id"],
            task["type"], task["voicetotal"],
            task["starttime"], ""])

    print row


if __name__ == "__main__":
    main()
