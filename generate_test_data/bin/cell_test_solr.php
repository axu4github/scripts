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
define('CURR_DIR', dirname(__FILE__));

require_once (CURR_DIR . "/../conf/conf.php");
require_once (CURR_DIR . "/../lib/formatHelper.class.php");
require_once (CURR_DIR . "/../lib/numberHelper.class.php");
require_once (CURR_DIR . "/../tools/Apache/Solr/Service.php");

try
{
    $host = "172.31.117.81";
    $port = "8983";
    $solr = new Apache_Solr_Service($host, $port, '/solr/smartv/');
    $params = array(
        "areaOfJob",
        "callCenter",
        "callNumber",
        "callType");
    $q = array();
    $o = array();
    $metaInfo = Config::getMetaInfo();
    $cellMetaData = FormatHelper::formatCellMetaData($metaInfo);
    $cellMetaData['plainText'] = "你好 夺冠 怒吼 谢谢 体育 夺冠 天使 不客气 比赛 运气 换位 表演 漫步 出场 策划";
    // 必选项 随机取出关键词部分
    $randKw = rand(2, 3); // 每次随机取出几个关键词, 最多能取出20个
    $kwTypeArr = array("plainText");
    $kwType = $kwTypeArr[array_rand($kwTypeArr, 1)]; // 随机从kwTypeArr中取出一个值
    $kwArr = explode(" ", $cellMetaData['plainText']);
    shuffle($kwArr);
    $kwArr = array_slice($kwArr, 1, $randKw);
    $kwResult = "";
    foreach ($kwArr as $kw)
    {
        $kwResult .= sprintf("%s:%s AND ", $kwType, $kw);
    }

    $kwResult = substr($kwResult, 0, -5);
    // 判断起始时间和结束时间大小
    $start = $cellMetaData['recordingStart'] / 1000;
    $end = $cellMetaData['recordingEnd'] / 1000;
    if ($start > $end) {
      $tmp = 0;
      $tmp = $start;
      $start = $end;
      $end = $tmp;
    }	

    echo sprintf("---->Start Date: %s \n", date("Ymd", $start / 1000)); 
    echo sprintf("---->End Date: %s \n", date("Ymd", $end / 1000));

    // 设置通话时间部分和通话时长,
    if (0)
    { // 是否将关键词加入fq中查询
        $q[] = $kwResult;
        $o['fq'] = sprintf("duration:[0 TO %d] AND recordingStart:[%d TO *] AND recordingEnd:[0 TO %d]",
            ($cellMetaData['duration'] + 1), ($start - 1), ($end + 1));
    } else {
        $o['fq'] = sprintf("duration:[0 TO %d] AND recordingStart:[%d TO %d] AND %s",
            ($cellMetaData['duration'] + 1), ($start - 1), ($end + 1), $kwResult); // 通过fq设置关键词
    }
    // 设置 呼叫类型，机构领域，（电话号码，坐席号，文件名不设置）
    $q[] = sprintf("callType:%s", $cellMetaData['callType']);
    $q[] = sprintf("areaOfJob:%s", $cellMetaData['areaOfJob']);
    $q[] = sprintf("callCenter:%s", $cellMetaData['callCenter']);

//    $q[] = sprintf("year:%s", $cellMetaData['year']);

//    $q = array("*:*");
    var_dump($q);
    var_dump($o);
    $result = $solr->search($q, 0, 20, $o);
    echo sprintf("NumberFound: %d  \n", $result->response->numFound);

}
catch (exception $e)
{
    die($e);
}

?>
