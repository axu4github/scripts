# -*- coding: utf-8 -*-

from quality_inspections import QualityInspection
import json
import time

""" 质检任务维护脚本 """


def main():
    qi = QualityInspection(redis_host="172.31.117.31")
    for (quality_id, quality_info_str) in qi.get_tasks().items():
        quality_info = json.loads(quality_info_str)
        print "{id}, {type}, {voicetotal}, {starttime}".format(
            id=quality_id,
            voicetotal=quality_info["voicetotal"],
            type=quality_info["type"],
            starttime=time.strftime(
                "%Y-%m-%d", time.localtime(quality_info["starttime"] / 1000))
        )


if __name__ == "__main__":
    main()
