# coding: utf-8

"""
[功能说明]
该脚本的功能是可以根据自定义规则，重写`csv`格式文件
可以通过`fieldnames`参数指定`csv`文件列名
重写规则在`reset_row(row, in_filename, out_filename)`方法中
  - row: 读到的当前行的值，若制定了`fieldnames`参数则为`dict`。若没有指定`fieldnames`参数则为`list`顺序和`csv`文件顺序一致。
  - in_filename: 输入文件名
  - out_filename: 输出文件名

[使用方法]
python reindex.py ${in_filename} ${out_filename}
"""

import csv
import sys
from datetime import datetime

# 默认列名称（共38列）
DEFAULT_FIELDNAMES = ["filename", "area_of_job", "start_time", "end_time", "duration", "callnumber", "rep_no", "rep_group", "agent_no", "account_no", "rep_team", "calltype", "number_of_record", "region", "project_list", "satisfaction", "qa_no", "summarize_group", "summarize_class",
                      "summarize_project", "summarize_content", "is_qa", "to_warehouse", "to_improvement", "isnormality", "type_of_service", "data_status", "data_status_2", "data_status_3", "group_leader", "cust_id", "cust_name", "audit_no", "phone_type", "verify_type", "staff_name", "bu_type", "rule_prompt"]


def reset_index(in_filename, out_filename, fieldnames=None, is_write_headers=False, *args, **kwds):
    """ 
    重写索引文件 

    [参数说明]
    `in_filename`: 原始索引文件名称
    `out_filename`: 输出索引文件名称
    `fieldnames`: 列名（要和`in_filename`文件列对的上）
    `is_write_headers`: `out_filename`文件是否写头（内容和顺序为`fieldnames`）
    """

    try:
        # 打开读文件句柄
        with open(in_filename, 'rb') as in_f:
            reader = csv.reader(in_f) if fieldnames is None else csv.DictReader(
                in_f, fieldnames=fieldnames)

            # 打开写文件句柄
            with open(out_filename, 'wb') as out_f:
                writer = csv.writer(out_f) if fieldnames is None else csv.DictWriter(
                    out_f, fieldnames=fieldnames)

                # 是否写头
                if is_write_headers:
                    writer.writeheader()

                # 读每行
                for row in reader:
                    writer.writerow(reset_row(row, in_filename,
                                              out_filename, *args, **kwds))
    except Exception as e:
        print "Error Message: [{0}]".format(e)
        return False

    return True


def reset_row(row, in_filename, out_filename, *args, **kwds):
    """
    重写一行

    [参数说明]
    `row`:  当前行内容。
            若已经配置`fieldnames`字段，则为一个 dict（乱序）；
            若没有配置`fieldnames`字段，则为一个 list（顺序和`in_filename`一致）。
    `in_filename`: 原始索引文件名称
    `out_filename`: 输出索引文件名称
    """

    # 重写`rep_group`列
    row["rep_group"] = row["rep_no"]

    # 重写 `start_time` 和 `end_time`列
    date_format = "%Y-%m-%d %H:%M:%S"

    # === 处理说明
    # out_filename -> "kf_kf01_20170322_1.index"
    # out_filename.split("_")[2] -> "20170322"
    dt = datetime.strptime(out_filename.split("_")[2], "%Y%m%d")

    # === 处理说明
    # row["start_time"] -> "'2017-02-20 12:00:00'"
    # row["start_time"].strip("''") -> "2017-02-20 12:00:00" # 去掉前后的单引号
    start_time = datetime.strptime(row["start_time"].strip("''"), date_format).replace(
        year=dt.year, month=dt.month, day=dt.day)
    end_time = datetime.strptime(row["end_time"].strip("''"), date_format).replace(
        year=dt.year, month=dt.month, day=dt.day)

    # 加上前后的单引号
    row["start_time"] = "'{0}'".format(start_time)
    row["end_time"] = "'{0}'".format(end_time)

    return row


if __name__ == '__main__':
    _, i_file, o_file = sys.argv
    reset_index(i_file, o_file, fieldnames=DEFAULT_FIELDNAMES)
