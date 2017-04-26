<?php

/**
 * 数字帮助
 *
 * @author axu
 * @version $Id$
 * @copyright Centrin, 10 July, 2014
 * @package default
 **/

class NumberHelper
{
    public static function randFloat($min, $max)
    { // 取得浮点型两个数中的随即数
        return $min + mt_rand() / mt_getrandmax() * ($max - $min);
    }

}
