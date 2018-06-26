# coding=utf-8

import unittest
import random
import time
import os
from hbase_client import HBaseClient
from solrcloud_client import SolrCloudClient
from configs import Config
from utils import Utils


class TestHBaseClient(unittest.TestCase):

    def generate_random_hbase_record(self):
        """ 随机创建 HBase 数据 """
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
        """ 初始化 """
        self.hbase_client = HBaseClient(
            Config.HBASE_HOST, Config.HBASE_TABLE)
        self.random_hbase_records = [
            (
                "random_row_key_20180625-103009_0.838398085891",
                {"cf:foo": "0.179806544721"}
            ),
            (
                "random_row_key_20180625-103009_0.0648745480584",
                {"cf:foo": "0.206042879869"}
            ),
            (
                "random_row_key_20180625-103009_0.96579555455",
                {"cf:foo": "0.0233687499447"}
            ),
            (
                "random_row_key_20180625-103009_0.330188225517",
                {"cf:foo": "0.515736624128"}
            ),
            (
                "random_row_key_20180625-103009_0.0994072251499",
                {"cf:foo": "0.583493900827"}
            ),
            (
                "random_row_key_20180625-103009_0.519030696533",
                {"cf:foo": "0.167216673505"}
            ),
            (
                "random_row_key_20180625-103009_0.953019825394",
                {"cf:foo": "0.717685314714"}
            ),
            (
                "random_row_key_20180625-103009_0.580058068272",
                {"cf:foo": "0.052202184166"}
            ),
            (
                "random_row_key_20180625-103009_0.882051079365",
                {"cf:foo": "0.652883882369"}
            ),
            (
                "random_row_key_20180625-103009_0.423149623297",
                {"cf:foo": "0.689676420661"}
            ),
        ]

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

    def test_03_delete_from_file(self):
        """ 测试根据文件删除数据 """
        row_number = 59
        filepath = "{0}/{1}{2}.txt".format(
            Config.BASE_DIR,
            time.strftime("%Y%m%d-%H%M%S", time.localtime()),
            random.random())
        rhr = [self.generate_random_hbase_record() for _ in range(row_number)]
        self.hbase_client.batch_put(rhr)

        for (row_key, value) in rhr:
            self.assertEqual(value, self.hbase_client.get(row_key))

        row_keys = [row_key for row_key, value in rhr]
        if Utils.put_file_contents(row_keys, filepath):
            deleted_filepath = Utils.get_deleted_filepath(filepath)
            try:
                self.assertEqual(
                    row_number, Utils.get_file_line_number(filepath))
                self.assertTrue(os.path.isfile(filepath))

                start = 2  # 从第几行开始执行
                self.hbase_client.set_batch_number(10)
                self.hbase_client.delete_from_file(filepath, start=start)

                self.assertEqual(
                    row_number - (start - 1),
                    Utils.get_file_line_number(deleted_filepath))
            except Exception as e:
                raise e
            finally:
                os.remove(filepath)
                os.remove(deleted_filepath)

        deleted_row_keys = row_keys[start - 1:]
        # 验证已经被删除的数据，是否已删除
        for row_key in deleted_row_keys:
            self.assertEqual({}, self.hbase_client.get(row_key))

        # 验证没有被删除的是数据，是否未删除
        none_deleted_rhr = rhr[0:start - 1]
        for (row_key, value) in none_deleted_rhr:
            self.assertEqual(value, self.hbase_client.get(row_key))

            # 若验证成功则删除未删除的数据
            self.hbase_client.delete(row_key)
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
        try:
            self.assertTrue(
                Utils.put_file_contents(
                    self.contents, self.filepath, mode=Config.FILE_APPEND))
            self.assertEqual(
                len(self.contents) * 2,
                Utils.get_file_line_number(self.filepath))
        except Exception as e:
            raise e
        finally:
            os.remove(self.filepath)


class TestSolrCloudClient(unittest.TestCase):
    """ 测试 SolrCloud 客户端类 """

    def setUp(self):
        """ 初始化 """
        self.solrcloud_client = SolrCloudClient(Config.SOLR_NODES)
        self.docs = [
            {"id": "test_solr_20180625-102654_0.341970530101"},
            {"id": "test_solr_20180625-102654_0.777160406839"},
            {"id": "test_solr_20180625-102654_0.36220746147"},
            {"id": "test_solr_20180625-102654_0.150193855602"},
            {"id": "test_solr_20180625-102654_0.0414728164608"},
            {"id": "test_solr_20180625-102654_0.844821599731"},
            {"id": "test_solr_20180625-102654_0.945288912237"},
            {"id": "test_solr_20180625-102654_0.956059157918"},
            {"id": "test_solr_20180625-102654_0.171609738001"},
            {"id": "test_solr_20180625-102654_0.0643217980109"}
        ]

    # def generate_random_doc(self):
    #     return {
    #         "id": "{0}_{1}_{2}".format(
    #             "test_solr",
    #             time.strftime("%Y%m%d-%H%M%S", time.localtime()),
    #             random.random()
    #         )}

    def doc_exists(self, doc_id):
        response = self.solrcloud_client.search("id:{0}".format(doc_id))
        return response["numFound"] == 1

    def test_00_create_docs(self):
        """ 测试创建索引 """
        self.assertTrue(self.solrcloud_client.create(self.docs))

    def test_01_search_docs(self):
        """ 测试检索 """
        for doc in self.docs:
            self.assertTrue(self.doc_exists(doc["id"]))

    def test_02_download_docs(self):
        """ 测试下载索引 """
        download_file = "{0}/{1}{2}.txt".format(
            Config.BASE_DIR,
            time.strftime("%Y%m%d-%H%M%S", time.localtime()),
            random.random())

        query = "id: test_solr_20180625-102654_0.*"

        self.assertTrue(self.solrcloud_client.download(
            query, download_file))
        self.assertTrue(os.path.isfile(download_file))
        self.assertEqual(
            Utils.get_file_line_number(download_file),
            self.solrcloud_client.search(query=query).numFound)

        os.remove(download_file)

        self.assertFalse(os.path.exists(download_file))

    def test_03_delete_docs(self):
        """ 测试删除索引 """
        for doc in self.docs:
            doc_id = doc["id"]
            self.assertTrue(self.solrcloud_client.delete(doc_id=doc_id))
            self.assertFalse(self.doc_exists(doc_id))


if __name__ == "__main__":
    unittest.main()
