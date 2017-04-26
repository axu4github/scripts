<?php

/**
 * 格式化信息帮助
 *
 * @author axu
 * @version $Id$
 * @copyright Centrin, 10 July, 2014
 * @package default
 **/

#date_default_timezone_set('Asia/Chongqing');
#require_once ("./numberHelper.class.php");

class FormatHelper
{
    public static function formatCellMetaData($metaInfo, $totalNumber = null, $currentNumber = null)
    {
        $cellMetaData = array();
        $metaKeys = array_keys($metaInfo); // 得到所有属性
        $index_i = 1; 
        foreach ($metaKeys as $metaKey) { // 循环便利所有属性
            $metaVal = ""; // 单条属性最后值
            $metaAttr = $metaInfo[$metaKey];
            $metaCellNumber = $metaAttr['cellNumber'] <= 0 ? 1 : $metaAttr['cellNumber']; // 判断属性值有多少个
            $metaValSeparator = $metaAttr['metaValSeparator'];
            $metaCellSeparator = $metaAttr['cellValSeparator'];
            $metaCellScope = is_array($metaAttr['cellScope']) ? $metaAttr['cellScope'] : array($metaAttr['cellScope']); // 属性值域
            if (
                isset($metaAttr['rate']) &&   
                isset($metaAttr['rateArr']) &&
                !empty($metaAttr['rateArr']) &&
                $totalNumber > 0 && 
                $currentNumber >= 0 && 
                $totalNumber >= $currentNumber &&
                $currentNumber <= ($totalNumber * $metaAttr['rate'])
            ) { 
                $rateArr = $metaAttr['rateArr'];
                $metaVal = $rateArr[array_rand($rateArr, 1)];
            } else {
                for ($i = 0; $i < $metaCellNumber; $i++) {
                    $cellVal = "";
                    foreach ($metaCellScope as $cellScope) {
                        foreach ($cellScope as $type => $scope) {
                            $tmpVal = "";
                            switch ($type) {
                                case 'int': // 处理整形类数据
                                    list($min, $max) = explode(',', $scope);
                                    if ($min > $max) {
                                        $tmp = $min;
                                        $min = $max;
                                        $max = $tmp;
                                    }

                                    $tmpVal = rand($min, $max);
                                    break;
                                case 'float': // 处理浮点型类数据
                                    list($min, $max) = explode(',', $scope);
                                    if ($min > $max) {
                                        $tmp = $min;
                                        $min = $max;
                                        $max = $tmp;
                                    }

                                    $tmpVal = sprintf("%.2f", NumberHelper::randFloat($min, $max));
                                    break;
                                case 'date': // 处理日期类型数据
                                    list($start, $end) = explode(',', $scope); // 取得开始时间和结束时间
                                    $startTime = strtotime($start);
                                    $endTime = strtotime($end);
                                    $startTimeResult = $startTime;
                                    $endTimeResult = $endTime;
                                    if ($startTime > $endTime) { // 如果起始时间大于结束时间, 则倒置
                                        $startTimeResult = $endTime;
                                        $endTimeResult = $startTime;
                                    }

                                    // 两个时间段中，随机取一天
                                    $timeDiff = $endTimeResult - $startTimeResult;
                                    $dayDiff = intval($timeDiff / 86400);
                                    $randDay = rand(1, $dayDiff);
                                    $tmpVal = $startTimeResult + ($randDay * 86400);
                                    break;
                                case 'oneDay': // 获得一个日期中随机一个时刻
                                    $perDaySeconds = 86400;
                                    $randSeconds = rand(1, $perDaySeconds - 1);
                                    $tmpVal = strtotime($scope) + $randSeconds;
                                    // $tmpVal = date("Y-m-d H:i:s", $tmpVal);
                                    break;
                                default: // 处理字符串类数据
                                    $tmpVal = $scope[array_rand($scope, 1)];
                                    break;
                            }

                            $cellVal .= sprintf("%s%s", $tmpVal, $metaCellSeparator);
                        }
                    }
                }

                $cellVal = strlen($metaCellSeparator) == 0 ? $cellVal : substr($cellVal, 0,
                    strlen($metaCellSeparator) * -1); // 去除字符串最后的metaCellSeparator
                $metaVal .= sprintf("%s%s", $cellVal, $metaValSeparator);
            }

            $metaVal = strlen($metaValSeparator) == 0 ? $metaVal : substr($metaVal, 0,
                strlen($metaValSeparator) * -1); // 去掉结果的最后一个metaValSeparator

            $index_i++;
            $cellMetaData[$metaKey] = $metaVal;
        }

        return $cellMetaData;
    }
}
