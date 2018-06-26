# coding=utf-8

import os
import commands
from configs import Config


class Utils(object):
    """ 工具类 """

    @staticmethod
    def put_file_contents(contents, filepath, mode=None, content_parser=None):
        f = None
        if mode is None:
            f = open(filepath, "w")
        elif mode == Config.FILE_APPEND:
            f = open(filepath, "a")
        else:
            raise Exception("MODE [{0}] Not Found.".format(mode))

        try:
            if f is None:
                raise Exception("""
                    Init File Handle Error. Please Check Mode Parameter.
                """.strip())

            for content in contents:
                if content_parser is not None:
                    content = content_parser(content)

                f.write("{0}{1}".format(content, os.linesep))
        except Exception as e:
            raise e
        finally:
            f.close()

        return True

    @staticmethod
    def get_file_line_number(filepath):
        line_number = 0
        if os.path.isfile(filepath):
            cmd = "wc -l {0}".format(filepath)
            status, output = commands.getstatusoutput(cmd)
            if status == 0:
                line_number = int(output.strip().split(" ")[0])
            else:
                raise Exception(output)

        return line_number

    @staticmethod
    def get_deleted_filepath(filepath):
        return "{0}.deleted".format(filepath)
