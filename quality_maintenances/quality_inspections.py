# -*- coding: utf-8 -*-

import redis


class QualityInspection:
    """ 质检类 """

    def __init__(self, *args, **kwargs):
        redis_host = kwargs.get("redis_host", "localhost")
        redis_port = kwargs.get("redis_port", 6379)
        redis_db_index = kwargs.get("db", 0)
        # 初始化 redis 连接
        self.redis = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db_index)

    def get_tasks(self):
        """
        获取所有质检任务

        数据结构样例：
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
        return self.redis.hgetall("tasklist_history")
