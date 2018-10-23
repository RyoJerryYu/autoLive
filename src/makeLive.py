# -*- coding: utf-8 -*-
'''直播信息相关函数
一次直播信息记录在live类中
'''
import os
from datetime import datetime, timedelta, timezone

from src.utitls import errmsg, tracemsg, logmsg
from src.liveScheduler import Live
from src.Configs import CONFIGs


def __analyse_live_list(text):
    '''分析时间表text并输出直播信息列表

    时间表text每行为 time@liver@site@title
    site可省略，可用值只能在sites中选择，默认为YouTube
    title可省略，默认为 liver+' 转播'，如果参数过多不报错，title默认为最后一个参数

    Args:
        text: str,
    
    Returns:
        lives: list, live类列表
    '''
    lives = []
    for line in text.split('\n'):
        try:
            line = line.strip()
            # 跳过注释
            if len(line) == 0 or line[0] == '#':
                continue
            live = Live.livefScheduleTxt(line)
            lives.append(live)
        except Exception as e:
            txt = ''
            if len(str(e).strip()) == 0:
                txt = '\n'+tracemsg(e)
            errmsg('schedule', str(e)+txt)
    return lives


def makeLives():
    '''读取schedule.txt，解析，并输出直播信息列表

    Returns:
        lives: live类列表
    '''
    # Read config
    config = CONFIGs()
    SCHEDULE_TXT_PATH = config.SCHEDULE_TXT_PATH

    # Get live list
    text = ""
    with open(SCHEDULE_TXT_PATH, encoding='utf-8') as file:
        text = file.read()
    lives = __analyse_live_list(text)
    lives.sort(key=lambda live:live.time)

    return lives
