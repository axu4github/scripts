# -*- coding: utf-8 -*-

import redis


class QualityInspection:
    """ 质检类 """

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

    def get_task_detail(self, task_id, start_time):
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

    def get_all_tasks(self, is_now=True):
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
        if is_now:
            return self.redis.hgetall(self.task_now)
        else:
            return self.redis.hgetall(self.task_history)
