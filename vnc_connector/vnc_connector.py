#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import commands
import click
import sys
reload(sys)
sys.setdefaultencoding('utf8')


"""
创建和远程服务器的基于SSH连接，用于VNC连接使用。（解决Mac OSX使用VNC无法连接Linux服务器问题）

参考地址：https://stackoverflow.com/questions/41833435/vnc-mac-os-x-and-linux-connection-refused-by-computer/41840096#41840096
"""

HOST = "localhost"
PORT = 5901
COMMAND = """
    /usr/bin/ssh -NTf -L {port}:{host}:{port} {remote_user}@{remote_host}
"""


def start(remote_host, remote_user):
    """启动SSH连接"""
    start_command = COMMAND.format(
        port=PORT, host=HOST,
        remote_user=remote_user, remote_host=remote_host
    )

    click.echo("启动SSH服务命令: " + start_command)
    os.system(start_command)
    # (p_status, out) = commands.getstatusoutput(start_command)
    (_, out) = status()
    click.echo("当前SSH进程ID: " + out.split()[1])


def status():
    """查看SSH进程状态"""
    status_command = "ps aux | grep {port} | grep -v grep".format(port=PORT)
    return commands.getstatusoutput(status_command)


def stop():
    """停止已经启动的进程"""
    (p_status, out) = status()
    if 0 == p_status:
        process_id = out.split()[1]
        click.echo("原有SSH服务进程ID: " + process_id)
        stop_command = "kill -9 {pid}".format(pid=process_id)
        (p_status, out) = commands.getstatusoutput(stop_command)
        # print status, out


def restart(remote_host, remote_user):
    """重启SSH服务"""
    stop()
    start(remote_host, remote_user)


@click.command()
@click.option("--host", help="远程服务器主机名或者IP地址")
@click.option("--user", help="连接远程服务器使用用户")
def main(host, user):
    """
    创建和远程服务器的基于SSH连接，用于VNC连接使用（解决Mac OSX使用VNC无法连接Linux服务器问题）。

    启动以后 VNC Viewer 可以使用：localhost:5901 连接远程服务器
    """
    restart(host, user)


if __name__ == '__main__':
    main()
