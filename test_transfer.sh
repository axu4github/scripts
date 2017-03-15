#!/bin/bash

# ===
# 功能说明
#
# 测试语音文件转码，给一个需要验证是否可以转码的文件目录，脚本会将目录（一级）下的所有文件进行转码测试。
# ===

contents=$1
suffix="V3"
work_dir="work"

# 确认环境
echo " ==="
echo " - 确认环境"
echo " - contents: ${contents}"
echo " - work_dir: ${work_dir}"
echo " ==="

# 初始化工作目录
if [ ! -d ${work_dir} ]; then
    mkdir ${work_dir}
fi

# 处理文件
for file in `ls ${contents} | grep .${suffix}`
do
    src_file="${contents}/${file}"
    tmp_file="${work_dir}/${file}.vox"
    dest_file="${work_dir}/${file}.wav"

    echo ""
    echo " === Start Transfer File: ${file}"

    echo " - Rename File: ${file}"
    rename_command="cp ${src_file} ${tmp_file}"
    echo " - Execut Rename Command: ${rename_command}"
    `${rename_command}`

    start_transfer_time=$(date +%s)
    echo " - Transfer File: ${tmp_file}"    
    transfer_command="sox ${tmp_file} -b 16 -r 8000 ${dest_file}"
    echo " - Execut Transfer Command: ${transfer_command}"
    `${transfer_command}`
    end_transfer_time=$(date +%s)
    execut_time=$(( ${end_transfer_time} - ${start_transfer_time} ))
    echo " - Execut Transfer Time: ${execut_time}s"

    echo " - Clear Temp File: ${tmp_file}"
    remove_command="rm -rf ${tmp_file}"
    echo " - Execut Clear Command: ${remove_command}"
    `${remove_command}`
done

echo ""
echo "-EOF-"    

