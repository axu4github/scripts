# coding=utf-8

import click
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# Click 模块配置
CLICK_CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"],
    terminal_width=100)

CONTENT_SEPARATOR = "\t"
ROLE_SERVICE = "坐席"
ROLE_CUSTOMER = "客户"


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.help_option("-h", "--help", help="使用说明")
def cli():
    """
    HBase 维护脚本

    获取帮助信息请执行 python hbase_maintenances.py --help
    """
    pass


def gbk_to_utf8(_str):
    return _str.decode("gbk").encode("utf-8")


def format_voice_content(voice_content):
    format_result = []
    if len(voice_content) > 0:
        voice_content, temp = list(enumerate(voice_content)), []
        for (i, line) in voice_content:
            if i == 0:
                format_result.append(line[0])
            else:
                start, end, plaintext, curr_role = line
                if i == 1:
                    temp = line
                else:
                    pre_voice_content = voice_content[i - 1][1]
                    pre_role = pre_voice_content[3]
                    if curr_role == pre_role:
                        temp[1] = end
                        temp[2] = "{0} {1}".format(temp[2], plaintext)
                    else:
                        temp[1] = pre_voice_content[1]
                        format_result.append("\t".join(temp))
                        temp = line

        if len(temp) > 0:
            format_result.append("\t".join(temp))

        print("\n".join(format_result))

    return format_result


@cli.command(short_help="格式化语料")
@click.help_option("-h", "--help", help="使用说明")
@click.option("--src", default=None, help="需要格式化的语料文件")
@click.option("--dest", default=None, help="格式化后输出文件")
def format(src, dest):
    if not os.path.exists(src) and os.path.isfile(src):
        raise Exception(
            "File Path: [{0}] is not Exists or is not File.".format(src))

    with open(src, "r") as f:
        voice_contents = []
        for line in f:
            splited = line.strip().split(CONTENT_SEPARATOR)
            if len(splited) == 1 and splited[0].endswith(".wav"):
                if len(voice_contents) != 0:
                    format_voice_content(voice_contents)
                    voice_contents = []

                voice_contents.append(splited)
            else:
                splited[2] = gbk_to_utf8(splited[2])
                splited[3] = gbk_to_utf8(splited[3])
                voice_contents.append(splited)

        if len(voice_contents) != 0:
            format_voice_content(voice_contents)


if __name__ == "__main__":
    cli()
