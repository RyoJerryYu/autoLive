# -*- coding: utf-8 -*-
import os
import re
from src.utitls import logmsg, errmsg, RunCMD
import json


def get_m3u8(url_live, live_quality):
    '''获得YouTube直播的m3u8地址

    调用youtube-dl，获得清晰度列表，
    并返回其中清晰度不高于live_quality的最高清晰度m3u8。

    Args:
        url_live: str, 直播间的url
        live_quality: int, 最高清晰度，返回的m3u8清晰度不会高于此值
    
    Returns:
        m3u8_url: str, 直播的m3u8地址
    
    Raise:
        Exception
    '''
    # 获取清晰度
    out, err, errcode = RunCMD('youtube-dl --no-check-certificate -j {}'.format(url_live))
    out = out.decode('utf-8') if isinstance(out, (bytes, bytearray)) else out
    if errcode != 0:
        raise Exception('youtube-dl不正常返回，code={}'.format(errcode))
    
    try:
        vDict = json.loads(out)
    except Exception:
        raise Exception('清晰度列表无法用json解析')
    
    try:
        # 按清晰度由小到大排序
        vDict['formats'].sort(key=lambda live_format : live_format['height'])

        count = -1
        if live_quality != 0:
            for live_format in vDict['formats']:
                if live_format['height'] <=  live_quality:
                    count += 1 # 指向不大于所选择清晰度的最大值
                else:
                    break
            if count == -1:
                count = 0 # 选择清晰度小于最小清晰度时，返回最小清晰度
        else:
            count = -1 # 自动使用最高清晰度时，返回最后一组live_format
        
        # 获取m3u8
        m3u8_url = vDict['formats'][count]['url']
        logmsg('获得直播源m3u8地址：\n{m3u8}'.format(m3u8=m3u8_url))
        return m3u8_url
    except Exception:
        raise Exception('解析清晰度时格式出错，vDict:\n{}'.format(json.dumps(vDict, ensure_ascii=False, indent=2)))


def push_stream(url_rtmp, url_live, url_m3u8, command):
    '''调用ffmpeg将url_rtmp推至url_rtmp

    Args:
        url_rtmp:
        url_live: 仅用于记录
        url_m3u8:
        command: str, 推流命令
    '''
    logmsg('开始推流\nusing push_stream in Youtube\n{}\n{}\n{}\n{}\n'.format(url_rtmp,url_live,url_m3u8,command))
    command = command.format(url_m3u8, url_rtmp)
    out, err, errcode = RunCMD(command)
    logmsg('结束推流')
    return out, err, errcode

