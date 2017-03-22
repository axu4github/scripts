# coding: utf-8

import csv

# 默认列名称（共38列）
DEFAULT_FIELDNAMES = ["filename", "area_of_job", "start_time", "end_time", "duration", "callnumber", "rep_no", "rep_group", "agent_no", "account_no", "rep_team", "calltype", "number_of_record", "region", "project_list", "satisfaction", "qa_no", "summarize_group", "summarize_class",
                      "summarize_project", "summarize_content", "is_qa", "to_warehouse", "to_improvement", "isnormality", "type_of_service", "data_status", "data_status_2", "data_status_3", "group_leader", "cust_id", "cust_name", "audit_no", "phone_type", "verify_type", "staff_name", "bu_type", "rule_prompt"]


def reset_index(in_filename, out_filename, fieldnames=None, is_write_headers=False, *args, **kwds):
    """ 
    重写索引文件 

    [参数说明]
    `in_filename`: 原始索引文件
    `out_filename`: 输出索引文件
    `fieldnames`: 列名（要和`in_filename`文件列对的上）
    `is_write_headers`: `out_filename`文件是否写头（内容和顺序为`fieldnames`）
    """

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
                writer.writerow(reset_row(row))


def reset_row(row):
    """
    重写一列

    [参数说明]
    `row`:  当前行内容。
            若已经配置`fieldnames`字段，则为一个 dict（乱序）；
            若没有配置`fieldnames`字段，则为一个 list（顺序和`in_filename`一致）。
    """

    row["rep_group"] = row["rep_no"]
    return row


if __name__ == '__main__':
    file = 'kf_kf01_20170220_1.index'
    new_file = 'kf_kf01_20170220_1.index.new'

    reset_index(file, new_file, fieldnames=DEFAULT_FIELDNAMES)
