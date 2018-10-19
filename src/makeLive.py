# -*- coding: utf-8 -*-
'''直播信息相关函数
一次直播信息记录在live类中
'''
import os
from datetime import datetime, timedelta, timezone
import configparser

from src.utitls import errmsg, tracemsg, logmsg
from src.login_bilibili import login_bilibili
from src.liveScheduler import Live


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


def __make_schedule_post_txt(lives):
    '''读取lives列表，输出用于发动态的时间表字符串
    '''
    txt = '今日转播：\n时间均为日本时区\n'
    for live in lives:
        txt += '{}, {}, {}\n{}\n\n'.format(
            live.time.strftime(r'%m.%d %H:%M'),
            live.liver,
            live.site,
            live.title
        )
    return txt


def makeLives(CONFIG_PATH):
    '''读取schedule.txt，解析，并输出直播信息列表

    Args:
        CONFIG_PATH: str, config.ini路径
    
    Returns:
        lives: live类列表
    '''
    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    SCHEDULE_TXT_PATH = config.get('basic', 'SCHEDULE_TXT_PATH')

    # Get live list
    text = ""
    with open(SCHEDULE_TXT_PATH, encoding='utf-8') as file:
        text = file.read()
    lives = __analyse_live_list(text)
    lives.sort(key=lambda live:live.time)

    return lives


def post_schedule(CONFIG_PATH, lives):
    '''发送时间表动态

    Args:
        CONFIG_PATH: config.ini路径
        lives: 直播信息列表
    
    Returns:
        0: 正常发送动态
        -1: 发送动态过程中出错
    '''
    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')

    # Post dynamic
    try:
        schedule_post_txt = __make_schedule_post_txt(lives)
        b = login_bilibili(COOKIES_TXT_PATH)
        b.send_dynamic(schedule_post_txt)
    except Exception as e:
        txt = ''
        if len(str(e).strip()) == 0:
            txt = '\n'+tracemsg(e)
        errmsg('schedule', str(e)+txt)
        return -1
    return 0