# -*- coding: utf-8 -*-

import redis
import time
import json


class QualityTask:
    """ 质检任务类 """

    def __init__(self, *args, **kwargs):
        # redis 主机名 或者 IP 地址
        redis_host = kwargs.get("redis_host", "localhost")
        # redis 端口号
        redis_port = kwargs.get("redis_port", 6379)
        # redis DB 序号
        redis_db_index = kwargs.get("db", 0)
        # 质检任务历史信息队列名称
        self.task_history = kwargs.get("task_history", "tasklist_history")
        # 质检任务信息队列名称
        self.task_now = kwargs.get("task_now", "tasklist")

        # 初始化 redis 连接
        self.redis = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db_index)

    def _flat(self, tasks=None):
        """
        将原始格式压平（类似 Spark 的 flatMap）并格式化如下几列内容

        1. 添加一列 唯一标识 以便用来之后获取 质检任务详情使用
        2. 将 开始时间 (starttime) 和 结束时间 (endtime) 转换为 "%Y-%m-%d %H:%M:%S" 格式
        3. 将 质检编号 (id) 转换为 纯数字 (现在若是常规质检 id 字段的格式为 "{id}_{time}")
        """

        formated = []
        for (task_id, task) in tasks.items():
            tmp = json.loads(task)
            tmp["id"] = self._format_id(task_id)
            tmp["unique"] = "{start_time}_{id}".format(
                id=tmp["id"],
                start_time=self._format_time(tmp["starttime"], "%Y%m%d"))
            tmp["starttime"] = self._format_time(tmp["starttime"])
            tmp["endtime"] = self._format_time(tmp["endtime"])
            formated.append(tmp)

        return formated

    def _format_id(self, task_id=None):
        """ 格式化 质检编号 """
        return task_id.split("_")[0]

    def _format_time(self, _time=None, time_format="%Y-%m-%d %H:%M:%S"):
        """ 格式化 时间 """
        return time.strftime(time_format, time.localtime(_time / 1000))

    def get_all(self, is_now=True):
        """
        获取所有质检任务

        返回数据结构样例：
        {
            '353_2017-02-17': '{"createtime": "2017-08-16 13:54:28",
                                "status": "E",
                                "voicetotal": 0,
                                "nodename": "node32",
                                "type": "D",
                                "starttime": 1503027900329,
                                "endtime": 1503027900697}',
            ...,
        }
        """
        tasks = {}
        if is_now:
            tasks = self.redis.hgetall(self.task_now)
        else:
            tasks = self.redis.hgetall(self.task_history)

        return self._flat(tasks)

    def get_detail(self, task_id, start_time):
        """
        获取质检任务详细信息

        返回数据结构样例：
        {
            'write_reprot_start': '1504666410745',
            'get_voice_end': '1504666260109',
            'write_reprot_end': '1504666409136',
            'run_quality_start': '1504666260122',
            'run_quality_end': '1504666410540',
            'get_voice_start': '1504665540619'
        }
        """
        return self.redis.hgetall("TASK:{start_time}:{task_id}".format(
            start_time=start_time, task_id=task_id))
