<?php

/**
 * 建立solr测试数据脚本
 *
 * @author axu
 * @version $Id$
 * @copyright Centrin, 26 June, 2014
 * @package default
 **/

/**
 * Define DocBlock
 **/
date_default_timezone_set('Asia/Chongqing');
define("CURR_DIR", dirname(__FILE__));

require_once('vendor/autoload.php');

require_once (CURR_DIR . "/../conf/conf.php");
require_once (CURR_DIR . "/../lib/formatHelper.class.php");
require_once (CURR_DIR . "/../lib/numberHelper.class.php");
require_once (CURR_DIR . "/../tools/Apache/Solr/Service.php");

// 加载获取语音文件时长组件
require_once (CURR_DIR . "/../tools/getID3-1.9.12/getid3/getid3.php");

$climate = new League\CLImate\CLImate;
$climate->arguments->add([
    'type' => [
        'prefix' => 't',
        'longPrefix' => 'type',
        'description' => '建造数据类型，可是选择solr|hbase|test',
        'required' => true,
    ],
    'file' => [
        'prefix' => 'f',
        'longPrefix' => 'file',
        'description' => '索引数据写入文件的路径',
        'defaultValue' => NULL,
    ],
    'number' => [
        'prefix' => 'n',
        'longPrefix' => 'number',
        'description' => '创建索引数据总数量',
        'defaultValue' => NULL,
    ],
    'names' => [
        'prefix' => 'names',
        'longPrefix' => 'names',
        'description' => '根据已有的文件创建索引',
        'defaultValue' => NULL,
    ],
    'number_of_file' => [
        'prefix' => 'nof',
        'longPrefix' => 'number_of_file',
        'description' => '每个文件中索引文件数量',
        'defaultValue' => 500000,
    ],
    'special' => [
        'prefix' => 's',
        'longPrefix' => 'special',
        'description' => '特殊字段设置值，规则 "firstField:value&secondField:valye" 注意需要加""号',
        'defaultValue' => NULL,
    ],
    'help' => [
        'prefix' => 'h',
        'longPrefix' => 'help',
        'description' => '帮助',
        'noValue' => true,
    ],
]);

try {
    if ($climate->arguments->defined('help')) {
        $climate->usage();
        exit; 
    }

    $climate->arguments->parse();
    $type = $climate->arguments->get('type');
    $perFileNumber = $climate->arguments->get('number_of_file');
    $file = $climate->arguments->get('file');
    $limit = $climate->arguments->get('number');
    $names = $climate->arguments->get('names');
    if ($names != NULL) {
        $nameArr = file($names);
        $limit = count($nameArr);
    }

    $specialField = $climate->arguments->get('special');
    
} catch (Exception $e) {
    $climate->usage();
    exit;
}

try {
    // 需要配置字段
    $filenameField = "filename";
    $startTimeField = "start_time";
    $endTimeField = "end_time";

    $isWriteHeader = true; // 是否将头写入到创建文件中
    $isWriteBody = true; // 是否写内容到文件, 测试参数时使用
    $isPrintCellMetaData = false; // 打印格式化数据并退出，测试使用
    $cellValFormatPattern = "\"%s\","; // 单个元数据属性值组成格式，实际使用是 $cellVal .= sprintf($cellValFormatPattern, $val);
    $getID3 = new getID3(); // 初始化语音解析组件
    $metaInfo = Config::getMetaInfo();
    $keys = array_keys($metaInfo);  
    // 特殊字段设置值，规则 "firstField:value&secondField:valye" 注意需要加""号
    if ($specialField != NULL) {
        $specialFieldArr = explode("&", $specialField);
        foreach ($specialFieldArr as $sField) {
            $sArr = explode(":", $sField);
            $sKey = $sArr[0];
            $sVal = $sArr[1];

            if (in_array($sKey, $keys)) {
                if ($sKey == $startTimeField || $sKey == $endTimeField) {
                    $metaInfo[$sKey]['cellScope'] = array(array('oneDay' => $sVal));
                } else {
                    $metaInfo[$sKey]['cellScope'] = array(array('string' => array($sVal)));
                }
            }
        }
    }

    switch ($type) {
        case "solr":
            $isWriteHeader = true;
            $cellValFormatPattern = "\"%s\",";
            break;
        case "hbase":
            $isWriteHeader = false;
            $cellValFormatPattern = "%s&";
            break;
        case "test":
            $limit = 1;
            $isWriteHeader = false;
            $isWriteBody = false;
            $isPrintCellMetaData = true;
            break;
        default:
            usage();
            break;
    }

    $header = "";
    foreach ($keys as $key) {
        $header .= sprintf("%s,", $key);
    }

    $header = substr($header, 0, -1);
    $header = sprintf("%s\r\n", $header);
    $isGenerNewFile = true;
    $fileIndex = 1;
    for ($i = 1; $i <= $limit; $i++) {
        if ($isGenerNewFile) {
            if (1 == $fileIndex) {
                $fileName = sprintf("%s", $file);
            } else {
                $fileName = sprintf("%s_%d", $file, $fileIndex);
            }
            
            if ($isWriteHeader) {
                file_put_contents($fileName, $header);
            }
        }

        $isGenerNewFile = false;
        echo "$i \n";
        $cellMetaData = FormatHelper::formatCellMetaData($metaInfo, $limit, $i);
        if (1) { // 额外处理字段
            // 处理`id`
            $cellMetaData['id'] = sprintf("%s-%s", 
                $cellMetaData['area_of_job'],
                $cellMetaData['filename']
            );

            // 处理`end_time`
            $cellMetaData['end_time'] = $cellMetaData['start_time'] + $cellMetaData['duration'];
            

            // 处理`fileunique`
            $cellMetaData['fileunique'] = $cellMetaData['id'];

            // 处理 `years`, `months`, `days`
            $cellMetaData['years'] = date('Y', $cellMetaData['start_time']);
            $cellMetaData['months'] = date('m', $cellMetaData['start_time']);
            $cellMetaData['days'] = date('d', $cellMetaData['start_time']);

            // 将时间戳由秒级变为毫秒级
            $cellMetaData['end_time'] = $cellMetaData['end_time'] * 1000;
            $cellMetaData['start_time'] = $cellMetaData['start_time'] * 1000;
        }

        if (0) {
           $_filename = trim($nameArr[$i - 1]);
           $fileInfo = $getID3->analyze($_filename);   //分析文件
           $cellMetaData[$filenameField] = $_filename;
           $cellMetaData['duration'] = (int)$fileInfo['playtime_seconds']; // 获取真实录音时长
           $endTimeStamp = strtotime($cellMetaData[$startTimeField]) + $cellMetaData['duration']; // 根据开始时间和时长计算结束时间
           $cellMetaData[$endTimeField] = date("Y-m-d H:i:s", $endTimeStamp);
        }

        if ($isPrintCellMetaData) { // 打印格式化数据并退出，测试使用
            print_r($cellMetaData);
            exit;
        }

        $cellVal = "";
        foreach ($cellMetaData as $key => $val) {
            $cellVal .= sprintf($cellValFormatPattern, $val);
        }

        $cellVal = substr($cellVal, 0, -1);
        $cellVal = sprintf("%s\r\n", $cellVal);
        if ($isWriteBody) {
            file_put_contents($fileName, $cellVal, FILE_APPEND);
        }

        if (0 == ($i % $perFileNumber)) {
            $isGenerNewFile = true;
            $fileIndex++;
        }
    }
} catch (exception $e) {
    die($e);
}
