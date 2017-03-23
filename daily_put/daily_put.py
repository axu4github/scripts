# coding: utf-8

"""
[功能说明]
该脚本的功能主要是完成根据输入日期，完成创建输入日期的归集程序数据
其中工作项包括：
  - 原始数据包文件重命名（根据输入日期）
  - 原始数据索引文件重写（根据输入日期）（在`reindex.py`脚本中完成）
  - 原始索引文件（`start_time`, `end_time`）列内容更新（在`reindex.py`脚本中完成）
  - [额外] 原始索引文件（`rep_group`）列内容更新（在`reindex.py`脚本中完成）
  - 将修改后的`数据包文件`和`索引文件`写入指定执行目录
  - 创建完成文件（`.done`）
  - 将修改后的`数据包文件`和`索引文件`权限修改为`ftpuser`用户和用户组

[使用方法]
`python daily_put.py ${date}`
**注意** ${date}为8位日期。例如：`20170322`
"""

import sys
import os
import shutil
import commands
from reindex import reset_index

DEFAULT_FIELDNAMES = ["filename", "area_of_job", "start_time", "end_time", "duration", "callnumber", "rep_no", "rep_group", "agent_no", "account_no", "rep_team", "calltype", "number_of_record", "region", "project_list", "satisfaction", "qa_no", "summarize_group", "summarize_class",
                      "summarize_project", "summarize_content", "is_qa", "to_warehouse", "to_improvement", "isnormality", "type_of_service", "data_status", "data_status_2", "data_status_3", "group_leader", "cust_id", "cust_name", "audit_no", "phone_type", "verify_type", "staff_name", "bu_type", "rule_prompt"]


def fetch_datas(source_dir):
    # 索引文件后缀集合
    index_suffixs = [".index", ".idx"]
    datas = {}
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for f in filenames:
            file_info = os.path.splitext(f)
            # 根据文件后缀，找到索引文件
            if file_info[1] in index_suffixs:
                index_fullpath = "{0}{1}{2}".format(dirpath, os.path.sep, f)
                tar_fullpath = "{0}{1}{2}".format(
                    dirpath, os.path.sep, "{0}.tar".format(file_info[0]))
                # 判断索引文件对应的数据文件(.tar)是否存在
                if os.path.exists(tar_fullpath):
                    # 记录数据和索引文件同时存在的数据
                    area_of_job = os.path.basename(f).split("_")[0]
                    if area_of_job not in datas:
                        datas[area_of_job] = []

                    datas[area_of_job].append((tar_fullpath, index_fullpath))

    return datas


# 替换文件名中的日期
def change_file_name_by(date, filename):
    tmp = filename.split("_")
    tmp[2] = date
    return "_".join(tmp)


if __name__ == '__main__':
    _, date = sys.argv

    # 数据源目录
    source_dir = "soucre"

    # 生成中间数据的目录
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    # 处理时实际目录
    ftp_dir = "work"

    # 1. 获取所有需要处理的包
    print "=== 获取所有需要处理的包 {0}".format(source_dir)
    datas = fetch_datas(source_dir)
    # print datas

    # 2. 生成新数据
    for area_of_job, data in datas.iteritems():
        # 临时工作目录
        tmp_aoj_dir = "{0}{1}{2}{3}{4}".format(
            tmp_dir, os.path.sep, area_of_job, os.path.sep, date)
        if not os.path.exists(tmp_aoj_dir):
            os.makedirs(tmp_aoj_dir)

        # 实际处理目录
        dest_aoj_dir = "{0}{1}{2}{3}{4}".format(
            ftp_dir, os.path.sep, area_of_job, os.path.sep, date)
        if not os.path.exists(dest_aoj_dir):
            os.makedirs(dest_aoj_dir)

        print "=== 生成新数据 {0}-{1}".format(area_of_job, date)
        for tar_file, index_file in data:
            src_tar_file = tar_file
            src_index_file = index_file

            # 生成新的数据包（改名）
            dest_tar_file = "{0}{1}{2}".format(
                tmp_aoj_dir, os.path.sep, os.path.basename(change_file_name_by(date, tar_file)))

            print "  === 生成新的数据包 copy {0} {1}".format(src_tar_file, dest_tar_file)
            shutil.copyfile(src_tar_file, dest_tar_file)

            # 生成新的索引文件（改文件中的日期等字段内容）
            dest_index_file = "{0}{1}{2}".format(
                tmp_aoj_dir, os.path.sep, os.path.basename(change_file_name_by(date, index_file)))

            print "  === 生成新的索引文件（改文件中的日期等字段内容）{0} to {1}".format(src_index_file, dest_index_file)
            reset_index(src_index_file, dest_index_file,
                        fieldnames=DEFAULT_FIELDNAMES)

        # 3. 移动临时数据到处理文件夹中
        command = "mv {0}{1}* {2}".format(tmp_aoj_dir,
                                          os.path.sep, dest_aoj_dir)
        print "=== 移动临时数据到处理文件夹中 {0}".format(command)
        (status, output) = commands.getstatusoutput(command)
        if status != 0:
            print output

        # 4. 创建完成文件（.done）
        command = "touch {0}{1}{2}_{3}.done".format(
            dest_aoj_dir, os.path.sep, area_of_job, date)
        print "=== 创建完成文件 {0}".format(command)
        (status, output) = commands.getstatusoutput(command)
        if status != 0:
            print output

        # 5. 修改权限
        command = "chown ftpuser:ftpuser {0}{1}*".format(
            dest_aoj_dir, os.path.sep)
        print "=== 修改权限 {0}".format(command)
        (status, output) = commands.getstatusoutput(command)
        if status != 0:
            print output
