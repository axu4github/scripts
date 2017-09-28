# -*- coding: utf-8 -*-

from quality_inspections import QualityInspection
from prettytable import PrettyTable
import json
import time

""" 质检任务维护脚本 """


def main():
    row = PrettyTable()
    row.field_names = ["id", "type", "voicetotal", "starttime", "detail"]
    qi = QualityInspection(redis_host="172.31.117.31")
    # for (quality_id, quality_info_str) in qi.get_all_tasks(False).items():
    #     quality_info = json.loads(quality_info_str)
    #     start_time = quality_info["starttime"] / 1000
    #     full_date = time.strftime(
    #         "%Y-%m-%d %H:%M:%S", time.localtime(start_time))
    #     # simple_date = time.strftime("%Y%m%d", time.localtime(start_time))
    #     # details = qi.get_task_detail(quality_id, simple_date)
    #     r = ""
    #     # for (step, s_time) in details.items():
    #     #     print step, s_time
    #     #     s_time = int(s_time) / 1000
    #     #     r += "{step} => {time} \r".format(step=step, time=time.strftime(
    #     #         "%Y-%m-%d %H:%M:%S", time.localtime(s_time)))

    #     row.add_row([quality_id, quality_info["type"],
    #                  quality_info["voicetotal"], full_date, r])

    # print row
    print qi.get_all_tasks(False)


if __name__ == "__main__":
    main()
