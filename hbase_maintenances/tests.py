# coding=utf-8

import unittest
import random
import time
import os
from hbase_client import HBaseClient
from configs import Config
from utils import Utils


class TestHBaseClient(unittest.TestCase):

    def generate_random_hbase_record(self):
        prefix, cf = "random_row_key", "cf"
        row_key = b"{0}_{1}_{2}".format(
            prefix,
            time.strftime("%Y%m%d-%H%M%S", time.localtime()),
            random.random()
        )
        value = {
            b"{0}:foo".format(cf): b"{0}".format(random.random())}
        return (row_key, value)

    def setUp(self):
        self.hbase_client = HBaseClient(
            Config.HBASE_HOST, Config.HBASE_TABLE)
        self.random_hbase_records = [
            self.generate_random_hbase_record() for _ in range(10)]

    def test_00_put_hbase_record(self):
        """ 测试创建 HBase 记录 """
        for random_hbase_record in self.random_hbase_records:
            row_key, value = random_hbase_record

            self.assertTrue(self.hbase_client.put(row_key, value))
            self.assertEqual(value, self.hbase_client.get(row_key))

    def test_01_delete_hbase_record(self):
        """ 测试删除 HBase 记录 """
        row_key, value = self.random_hbase_records[0]

        self.assertTrue(self.hbase_client.delete(row_key))
        self.assertEqual({}, self.hbase_client.get(row_key))

    def test_02_batch_delete_hbase_records(self):
        """ 测试批量删除 HBase 记录 """
        row_keys = [rhr[0] for rhr in self.random_hbase_records]

        self.assertTrue(self.hbase_client.batch_delete(row_keys))

        for row_key in row_keys:
            self.assertEqual({}, self.hbase_client.get(row_key))


class TestUtils(unittest.TestCase):
    """ 测试工具类 """

    def setUp(self):
        self.contents = ["1", 2, "3", 4, "5", 0]
        self.filepath = "{0}{1}{2}".format(
            Config.BASE_DIR, os.sep,
            "test_put_file_contents_funciton.txt")

    def test_00_put_file_contents(self):
        self.assertTrue(
            Utils.put_file_contents(self.contents, self.filepath))
        self.assertEqual(
            len(self.contents), Utils.get_file_line_number(self.filepath))

    def test_01_put_file_contents_append_mode(self):
        self.assertTrue(
            Utils.put_file_contents(
                self.contents, self.filepath, mode=Config.FILE_APPEND))
        self.assertEqual(
            len(self.contents) * 2, Utils.get_file_line_number(self.filepath))


if __name__ == "__main__":
    unittest.main()
