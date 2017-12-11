# -*- coding: utf-8 -*-

import unittest
import copy
import json
from quality_tasks import QualityTask


class TestQualityTask(unittest.TestCase):

    def setUp(self):
        self.qt = QualityTask()
        self.one_tasks = {
            '170': '{"createtime":"2017-12-07 14:22:05","status":"D","voicetotal":333289,"nodename":"node69","type":"B","starttime":1512627840496}'
        }
        self.multiple_tasks = {
            '172': '{"createtime":"2017-12-07 15:13:06","status":"D","voicetotal":1152,"nodename":"node70","type":"C","starttime":1512630900591}',
            '170': '{"createtime":"2017-12-07 14:22:05","status":"D","voicetotal":333289,"nodename":"node69","type":"B","starttime":1512627840496}'
        }
        self.task_detail = [
            ('get_voice_start', '1512627840499'),
            ('get_voice_end', '1512629078544'),
            ('run_quality_start', '1512629096586'),
            ('run_quality_end', '1512634612716'),
            ('write_reprot_start', '1512634612720')
        ]

    def del_tasks_params(self, tasks, param):
        """ 删除任务信息中的某些项 """
        new_tasks = copy.copy(tasks)
        for (task_id, task_info) in tasks.items():
            task_info_dic = json.loads(task_info)
            del task_info_dic[param]
            new_tasks[task_id] = json.dumps(task_info_dic)

        return new_tasks

    def test_default_redis_connection(self):
        """ 测试 Redis 默认连接 """
        try:
            QualityTask().get_all()
        except Exception as e:
            self.assertTrue("Connection refused" in str(e))

    def test_one_tasks_flat(self):
        """ 测试只有一个任务时的 _flat() 方法 """
        tasks = self.qt._flat(self.one_tasks)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], "170")
        self.assertEqual(tasks[0]["unique"], "20171207_170")
        self.assertEqual(tasks[0]["createtime"], "2017-12-07 14:22:05")
        self.assertEqual(tasks[0]["status"], "D")
        self.assertEqual(tasks[0]["voicetotal"], 333289)
        self.assertEqual(tasks[0]["nodename"], "node69")
        self.assertEqual(tasks[0]["type"], "B")
        self.assertEqual(tasks[0]["starttime"], "2017-12-07 14:24:00")

    def test_multiple_tasks_flat(self):
        """ 测试多个任务时的 _flat() 方法 """
        tasks = self.qt._flat(self.multiple_tasks)

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["id"], "170")
        self.assertEqual(tasks[1]["id"], "172")
        self.assertEqual(tasks[1]["unique"], "20171207_172")
        self.assertEqual(tasks[1]["createtime"], "2017-12-07 15:13:06")
        self.assertEqual(tasks[1]["status"], "D")
        self.assertEqual(tasks[1]["voicetotal"], 1152)
        self.assertEqual(tasks[1]["nodename"], "node70")
        self.assertEqual(tasks[1]["type"], "C")
        self.assertEqual(tasks[1]["starttime"], "2017-12-07 15:15:00")

    def test_none_tasks_flat(self):
        """ 测试没有任务时得到 _flat() 方法 """
        # 测试不穿参数的情况
        tasks = self.qt._flat()

        self.assertEqual(len(tasks), 0)
        self.assertEqual(tasks, [])

        # 测试传入空参数的情况
        tasks = self.qt._flat({})

        self.assertEqual(len(tasks), 0)
        self.assertEqual(tasks, [])

    def test_add_interval(self):
        """ 测试时间间隔 """
        detail = self.qt._add_interval(self.task_detail)

        self.assertEqual(detail[0][2], 0)
        self.assertEqual(
            detail[1][2], float(detail[1][1]) - float(detail[0][1]))

    def test_miss_starttime_params_task_flat(self):
        """ 测试缺少 starttime 参数的 _flat() 方法 """
        new_one_tasks = self.del_tasks_params(self.one_tasks, "starttime")
        tasks = self.qt._flat(new_one_tasks)

        self.assertTrue("starttime" in tasks[0])
        self.assertEqual(tasks[0]["starttime"], 0)

    def test_miss_voicetotal_params_task_flat(self):
        """ 测试缺少 voicetotal 参数的 _flat() 方法 """
        new_one_tasks = self.del_tasks_params(self.one_tasks, "voicetotal")
        tasks = self.qt._flat(new_one_tasks)

        self.assertTrue("voicetotal" not in tasks[0])


if __name__ == "__main__":
    unittest.main()
