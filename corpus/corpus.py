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
FILE_APPEND = "FILE_APPEND"


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


def put_file_contents(contents, filepath, mode=None, content_parser=None):
        """ 将内容写入指定文件中 """
        f = None
        if mode is None:
            f = open(filepath, "w")
        elif mode == FILE_APPEND:
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


def format_voice_content(voice_content):
    """ 格式化一个语音文件的语料 """
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

    return format_result


@cli.command(short_help="格式化语料")
@click.help_option("-h", "--help", help="使用说明")
@click.option("--src", default=None, help="需要格式化的语料文件")
@click.option("--dest", default=None, help="格式化后输出文件")
def format(src, dest):
    if not os.path.exists(src) and not os.path.isfile(src):
        raise Exception(
            """
            Source File Path: [{0}] is not Exists or is not File.
            """.format(src.strip()))

    if dest is not None:
        if os.path.exists(dest):
            raise Exception(
                "Dest File Path: [{0}] is Exists.".format(dest))

    with open(src, "r") as f:
        voice_contents = []
        for line in f:
            splited = line.strip().split(CONTENT_SEPARATOR)
            if len(splited) == 1 and splited[0].endswith(".wav"):
                if len(voice_contents) != 0:
                    output = format_voice_content(voice_contents)
                    str_output = "\n".join(output)
                    voice_contents = []
                    if dest is None:
                        click.echo(str_output)
                    else:
                        put_file_contents(output, dest, FILE_APPEND)

                voice_contents.append(splited)
            else:
                splited[2] = gbk_to_utf8(splited[2])
                splited[3] = gbk_to_utf8(splited[3])
                voice_contents.append(splited)

        if len(voice_contents) != 0:
            output = format_voice_content(voice_contents)
            str_output = "\n".join(output)
            if dest is None:
                click.echo(str_output)
            else:
                put_file_contents(output, dest, FILE_APPEND)


if __name__ == "__main__":
    cli()
