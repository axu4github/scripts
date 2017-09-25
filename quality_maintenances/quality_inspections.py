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

        {
            '353_2017-02-17': '{"createtime":"2017-08-16 13:54:28","status":"E","voicetotal":0,"nodename":"node32","type":"D","starttime":1503027900329,"endtime":1503027900697}', 
            '211': '{"createtime":"2017-08-01 14:13:34","status":"F","voicetotal":"","nodename":"node32","type":"B","starttime":1501568820032,"endtime":1501568820051}', 
            '351_2017-02-14': '{"createtime":"2017-08-06 15:17:22","voicetotal":"","status":"E","nodename":"node32","type":"A","starttime":1502004060094,"endtime":1502004060097}', 
            '407': '{"createtime":"2017-09-06 10:18:26","starttime":1504664480568,"voicetotal":367,"status":"E","nodename":"node32","type":"C","endtime":1504665013601}',
            [...],
        }
        """
        return self.redis.hgetall("tasklist_history")
