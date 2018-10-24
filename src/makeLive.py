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


def saveLives(lives):
    '''读取live列表，以相应格式输入schedule.txt
    '''
    # Read config
    config = CONFIGs()
    SCHEDULE_TXT_PATH = config.SCHEDULE_TXT_PATH

    # Make text
    texts = [
        '# 时间表',
        '# 格式：',
        '# time@liver@site@title',
        '# time：直播时间，格式为HHMM，只接受未来24小时内的直播，检测出直播时间在运行程序之前时，会自动认为直播在运行程序第二天开始。',
        '# liver：只接受liveInfo.json中存在的liver名。（可自行按json格式添加到liveInfo文件中）',
        '# site：直播网站，目前只接受YouTube。而且不填默认为YouTube。',
        '# title：填入config.ini中直播间标题的title中，可选，不填默认为liver+"转播"',
        '',
        '# 例：',
        '# 1900@桜凛月@绝地求生',
        '# 2100@黒井しば',
        '# 2240@飛鳥ひな@YouTube',
        '# 0640@伏見ガク@YouTube@おはガク！',
    ]
    for live in lives:
        line = '{time}@{liver}@{site}@{title}'.format(
            time=live.time.strftime('%H%M'),
            liver=live.liver,
            site=live.site,
            title=live.title
        )
        texts.append(line)
    
    text = ''
    for line in texts:
        text += line+'\n'
    
    with open(SCHEDULE_TXT_PATH, 'w', encoding='utf-8') as file:
        file.write(text)