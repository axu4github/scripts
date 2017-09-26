# -*- coding: utf-8 -*-

from quality_inspections import QualityInspection
from prettytable import PrettyTable
import json
import time

""" 质检任务维护脚本 """


def main():
    row = PrettyTable()
    row.field_names = ["id", "type", "voicetotal", "starttime"]
    qi = QualityInspection(redis_host="172.31.117.31")
    for (quality_id, quality_info_str) in qi.get_all_tasks(False).items():
        quality_info = json.loads(quality_info_str)
        starttime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(quality_info["starttime"] / 1000))

        row.add_row([quality_id, quality_info["type"],
                     quality_info["voicetotal"], starttime])

    print row


if __name__ == "__main__":
    main()
