#!/bin/sh

# 将腾讯提供的数据移到语音识别目录中的脚本

tar_file=$1; # 腾讯给的数据文件全路径
tar_dir_name=$2; # 数据文件解压出来的目录名称
sttr_root_dir=$3; # 语音识别结果存放根目录全路径

# 设置默认值 
if [ -z "${sttr_root_dir}" ]; then
	sttr_root_dir="/mnt/mfs/voice_recognize_results";
fi

voiceconflict_dir="${sttr_root_dir}/voiceconflict";
voiceresult_dir="${sttr_root_dir}/voiceresult";
voicesence_dir="${sttr_root_dir}/voicesence";

# 设置默认值 
if [ -z "${tar_dir_name}" ]; then
	dir_name=${tar_file##*/};
	tar_dir_name=${dir_name%%.*};
fi

echo "腾讯数据文件路径: [${tar_file}].";
echo "数据文件解压出来的目录名称: [${tar_dir_name}].";
echo "语音识别结果存放根目录: [${sttr_root_dir}].";

sleep 5;

function make_sttr_dirs()
{
	run "mkdir -p ${voiceconflict_dir}";
	run "mkdir -p ${voiceresult_dir}";
	run "mkdir -p ${voicesence_dir}";
}

function run()
{
	cmd=$1;
	echo "---";
	echo "RUN COMMAND => [${cmd}]";
	${cmd};
}

function mv_tentcent_to_sttr_dir()
{
	tentcent_data_dir=$1;
	sttr_dir=$2;
	
	if [ ! -d "${tentcent_data_dir}" ]; then
		echo "ERROR !!! => ${tentcent_data_dir} IS NOT EXISTS.";
        	exit;
	fi

	if [ ! -d "${sttr_dir}" ]; then
                echo "ERROR !!! => ${sttr_dir} IS NOT EXISTS.";
                exit;
        fi

	run "mv ${tentcent_data_dir}/* ${sttr_dir}/";
}

# 解压文件
run "tar -xvf ${tar_file}";

# 查看解压文件内容
run "ls -l ${tar_dir_name}";

# 创建语音识别结果存放目录
make_sttr_dirs;

# 移动 抢插话(voiceconflict) 数据
tencent_conflict_dir="./${tar_dir_name}/conflict_text2";
mv_tentcent_to_sttr_dir "${tencent_conflict_dir}" "${voiceconflict_dir}";

# 移动 全文(voiceresult) 数据
tencent_emotion_dir="./${tar_dir_name}/emotion_text2";
mv_tentcent_to_sttr_dir "${tencent_emotion_dir}" "${voiceresult_dir}";

# 移动 静音(voicesence) 数据
tencent_silence_dir="./${tar_dir_name}/silence_text2";
mv_tentcent_to_sttr_dir "${tencent_silence_dir}" "${voicesence_dir}"

echo ""
echo "|| ------- ||"
echo "|| SUCCESS ||";
echo "|| ------- ||"

