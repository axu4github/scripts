# coding=utf-8

import happybase
import os
from utils import Utils
from configs import Config


class HBaseClient(object):
    """ HBase 客户端 """

    def __init__(self, host, table=None):
        self.batch_number = 10000
        self.connection = happybase.Connection(host)
        if table is not None:
            self._init_table(table)

    def _init_table(self, table):
        self.table = happybase.Table(table, self.connection)

    def put(self, row_key, value):
        """ 创建 HBase 记录 """
        self.table.put(row_key, value)
        return True

    def get(self, row_key, columns=None):
        """ 获取 HBase 记录 """
        return self.table.row(row_key, columns=columns)

    def delete_from_file(self, filepath, start=0):
        if not os.path.exists(filepath) and os.path.isfile(filepath):
            raise Exception(
                "File Path: [{0}] is not Exists or is not File.".format(
                    filepath))

        with open(filepath, "r") as f:
            i, buffer_data = 0, []
            for line in f:
                if i < start:
                    i += 1
                    continue
                else:
                    i += 1
                    # 若到达 self.batch_number 数量，则删除缓冲区数据
                    if len(buffer_data) == self.batch_number:
                        self.batch_delete_and_record(buffer_data, filepath)
                        buffer_data = []
                    # 若没到达 self.batch_number 数量，则继续写入缓冲区
                    else:
                        buffer_data.append(line.strip())

            # 删除最后不到 self.batch_number 的缓冲区数据
            if len(buffer_data) > 0:
                self.batch_delete_and_record(buffer_data, filepath)

        return True

    def delete(self, row_key, columns=None):
        """ 单条删除数据 """
        self.table.delete(row_key, columns=columns)
        return True

    def batch_delete(self, row_keys):
        """ 批量删除数据 """
        if len(row_keys) > 0:
            with self.table.batch() as bat:
                for row_key in row_keys:
                    bat.delete(row_key)

        return True

    def put_deleted_to_file(self, buffer_data, deleted_filepath):
        """ 将已经删除的数据记录到文件中 """
        return Utils.put_file_contents(
            buffer_data, deleted_filepath, mode=Config.FILE_APPEND)

    def batch_delete_and_record(self, buffer_data, filepath):
        """ 执行批量删除数据同时将已删除的数据记录到文件中 """
        return self.batch_delete(buffer_data) and \
            self.put_deleted_to_file(
                buffer_data,
                Utils.get_deleted_filepath(filepath))
