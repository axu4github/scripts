# coding: utf-8

import csv
import sys
import os
from datetime import datetime

# 默认列名称（共38列）
DEFAULT_FIELDNAMES = ["filename", "area_of_job", "start_time", "end_time", "duration", "callnumber", "rep_no", "rep_group", "agent_no", "account_no", "rep_team", "calltype", "number_of_record", "region", "project_list", "satisfaction", "qa_no", "summarize_group", "summarize_class",
                      "summarize_project", "summarize_content", "is_qa", "to_warehouse", "to_improvement", "isnormality", "type_of_service", "data_status", "data_status_2", "data_status_3", "group_leader", "cust_id", "cust_name", "audit_no", "phone_type", "verify_type", "staff_name", "bu_type", "rule_prompt", "field_01", "field_02", "field_03", "field_04", "field_05", "field_06", "field_07", "field_08", "field_09", "field_10", "field_11", "field_02", "field_13", "field_14"]


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
        csv.register_dialect(  
           'mydialect',  
           # delimiter = ',',  
           quotechar = '\'',  
           # doublequote = True,  
           # skipinitialspace = True,  
           # lineterminator = '\r\n',  
           # quoting = csv.QUOTE_MINIMAL
           quoting = csv.QUOTE_ALL
        )  

        # 打开读文件句柄
        with open(in_filename, 'rb') as in_f:
            reader = csv.reader(in_f) if fieldnames is None else csv.DictReader(
                in_f, fieldnames=fieldnames, dialect='mydialect')

            # 打开写文件句柄
            with open(out_filename, 'wb') as out_f:
                writer = csv.writer(out_f) if fieldnames is None else csv.DictWriter(
                    out_f, fieldnames=fieldnames, dialect='mydialect')

                # 是否写头
                if is_write_headers:
                    writer.writeheader()

                i = 1
                # 读每行
                for row in reader:
                    print i
                    writer.writerow(reset_row(row, in_filename,
                                              out_filename, *args, **kwds))
                    i = i + 1

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
    # out_filename -> "kf_20170322.index"
    dt = datetime.strptime(os.path.basename(out_filename).split("_")[1].split(".")[0], "%Y%m%d")

    # === 处理说明
    # row["start_time"] -> "'2017-02-20 12:00:00'"
    # row["start_time"].strip("''") -> "2017-02-20 12:00:00" # 去掉前后的单引号
    start_time = datetime.strptime(row["start_time"].strip("''"), date_format).replace(
        year=dt.year, month=dt.month, day=dt.day)
    end_time = datetime.strptime(row["end_time"].strip("''"), date_format).replace(
        year=dt.year, month=dt.month, day=dt.day)

    # 加上前后的单引号
    row["start_time"] = "{0}".format(start_time)
    row["end_time"] = "{0}".format(end_time)

    # 重写 `filename`列
    row["filename"] = "{0}_{1}".format(os.path.basename(out_filename).split("_")[1].split(".")[0], row["filename"].strip("''"))

    return row


if __name__ == '__main__':
    _, i_file, o_file = sys.argv
    reset_index(i_file, o_file, fieldnames=DEFAULT_FIELDNAMES)

