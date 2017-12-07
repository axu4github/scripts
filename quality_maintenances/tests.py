# -*- coding: utf-8 -*-

import unittest
from quality_tasks import QualityTask


class TestQualityTask(unittest.TestCase):

    def setUp(self):
        self.qt = QualityTask()
        self.one_tasks = {
            '170': '{"createtime":"2017-12-07 14:22:05","status":"D","voicetotal":333289,"nodename":"node69","type":"B","starttime":1512627840496}'
        }

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


if __name__ == "__main__":
    unittest.main()
