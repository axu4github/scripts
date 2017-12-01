# -*- coding: utf-8 -*-

import click
import time
import jieba
from functools import wraps
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# click 模块配置
CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"], terminal_width=100)
BASE_PATH = os.path.dirname(os.path.abspath("__file__"))
# 停用词文件路径
STOP_WORDS_FILE_PATH = "{}{}stop_words.txt".format(BASE_PATH, os.path.sep)
# 停用词数组
stop_words = [line.strip().decode("utf-8")
              for line in open(STOP_WORDS_FILE_PATH).readlines()]
TOPN = 800


def time_analyze(func):
    """ 装饰器 获取程序执行时间 """
    @wraps(func)
    def consume(*args, **kwargs):
        # 重复执行次数（单次执行速度太快）
        exec_times = 1
        start = time.time()
        for i in range(exec_times):
            r = func(*args, **kwargs)

        finish = time.time()
        print("{:<20}{:10.6} s".format(func.__name__ + ":", finish - start))
        return r

    return consume


@time_analyze
def file_get_contents(file_path):
    """ 从文件中获取查询条件 """
    context = ""
    with open(file_path) as f:
        for l in f.readlines():
            context += l

    return context


def file_put_contents(file_path, context):
    with open(file_path, "w") as f:
        f.write(context)


def stop_words_filter(words):
    return words not in stop_words


@time_analyze
def text_segmentation(context):
    kws = []
    for kw in jieba.cut(context):
        kws.append(kw.encode("utf-8"))

    return filter(stop_words_filter, kws)


@time_analyze
def extract_tags(context):
    import jieba.analyse
    jieba.analyse.set_stop_words(STOP_WORDS_FILE_PATH)
    tags = jieba.analyse.extract_tags(context, topK=TOPN)
    return tags


@click.command(context_settings=CLICK_CONTEXT_SETTINGS)
@click.option("--file_path", default=None, help="待分词的文本")
@click.option("--output", default=None, help="分词结果输出文件路径")
def main(file_path, output):
    if file_path is not None:
        context = file_get_contents(file_path)
        words = text_segmentation(context)
        words_str = " ".join(words)
        if output is None:
            click.echo("关键词数量: {}个".format(len(words)))
            click.echo(" === 关键词 ===")
            click.echo(words_str)
            click.echo(" === ")
        else:
            file_put_contents(output, words_str)

    print("-EOF-")


if __name__ == "__main__":
    main()
