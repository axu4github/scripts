# -*- coding: utf-8 -*-

import os
import redis
import time
import json
import glob


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
        # 质检任务日志文件路径
        self.log_file_pattern = "/mnt/mfs/upload/Logs/quality/*_{unique}.log"

        # 初始化 redis 连接
        self.redis = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db_index)

    def _flat(self, tasks=None):
        """
        将原始格式压平（类似 Spark 的 flatMap）并格式化如下几列内容

        1. 添加一列 唯一标识 以便用来之后获取 质检任务详情使用
        2. 将 开始时间 (starttime) 和 结束时间 (endtime) 转换为 "%Y-%m-%d %H:%M:%S" 格式
        3. 将 质检编号 (id) 转换为 纯数字 (现在若是常规质检 id 字段的格式为 "{id}_{time}")
        4. 获取 质检任务 对应 日志文件 的更新时间
        """

        formated = []
        for (task_id, task) in tasks.items():
            tmp = json.loads(task)
            tmp["id"] = self._format_id(task_id)
            if "starttime" in tmp:
                # $(start_time)_$(id)
                tmp["unique"] = "{}_{}".format(
                    self._format_timestamp(tmp["starttime"], "%Y%m%d"),
                    tmp["id"])
                tmp["starttime"] = self._format_timestamp(tmp["starttime"])
                tmp["log_modifiedtime"] = self._get_log_modified(tmp["unique"])

            if "endtime" in tmp:
                tmp["endtime"] = self._format_timestamp(tmp["endtime"])

            formated.append(tmp)

        return sorted(formated)

    def _format_id(self, task_id=None):
        """ 格式化 质检编号 """
        return task_id.split("_")[0]

    def _format_timestamp(self, _time=None, time_format="%Y-%m-%d %H:%M:%S"):
        """ 格式化 Timestamp 为 time_format 格式 """
        _time = int(_time)
        if len(str(_time)) > 10:
            _time = _time / 1000

        return time.strftime(time_format, time.localtime(_time))

    def _get_log_path(self, unique):
        """ 根据质检任务id，获取该任务日志文件路径 """
        return glob.glob(self.log_file_pattern.format(unique=unique))

    def _get_log_modified(self, unique):
        """ 根据 质检唯一标识 获取 质检任务 对应 日志文件 更新时间 """
        log_files = self._get_log_path(unique)
        if len(log_files) > 0:
            log_file = log_files[0]
        else:
            return "None File"

        return self._format_timestamp(os.stat(log_file).st_mtime)

    def get_all(self, is_now=True):
        """
        获取所有质检任务

        返回数据结构样例：
        {
            "353_2017-02-17": "{"createtime": "2017-08-16 13:54:28",
                                "status": "E",
                                "voicetotal": 0,
                                "nodename": "node32",
                                "type": "D",
                                "starttime": 1503027900329,
                                "endtime": 1503027900697}",
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
            "get_voice_start": "1504665540619",
            "get_voice_end": "1504666260109",
            "run_quality_start": "1504666260122",
            "run_quality_end": "1504666410540",
            "write_reprot_start": "1504666410745",
            "write_reprot_end": "1504666409136"
        }

        # 修改返回结果，增加按照时间排序。
        """
        details = self.redis.hgetall("TASK:{start_time}:{task_id}".format(
            start_time=start_time, task_id=task_id))

        return sorted(details.items(), lambda x, y: cmp(x[1], y[1]))
