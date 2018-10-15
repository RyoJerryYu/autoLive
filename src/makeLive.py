# -*- coding: utf-8 -*-
'''直播信息相关函数
一次直播以以下形式记录：
{
    'time': datetime.datetime, 用于任务开始的时间，即直播开始的时间
    'id': str, 用于scheduler中直播任务的唯一id，以 time_txt+liver 的形式保证唯一性
    'args': {
        'time': datetime.datetime, 直播开始的时间，与上面的'time'值相同
        'liver': str, 直播liver名，应在liveInfo.json中存在
        'site': str, 目前只支持YouTube
        'title': str, 用于直播间标题的可变内容
    }
}
'''
import os
from datetime import datetime, timedelta, timezone
import configparser

from utitls import errmsg, tracemsg, logmsg
from src.login_bilibili import login_bilibili


def __analyse_live_list(text):
    '''分析时间表text并输出直播信息列表

    时间表text每行为 time@liver@site@title
    site可省略，可用值只能在sites中选择，默认为YouTube
    title可省略，默认为 liver+' 转播'，如果参数过多不报错，title默认为最后一个参数

    Args:
        text: str,
    
    Returns:
        lives: list, 直播信息列表
    '''
    JST = timezone(timedelta(hours=+9), 'JST')
    sites = ['YouTube']
    lives = []
    for line in text.split('\n'):
        try:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            args = line.split('@')
            if len(args) < 2:
                raise Exception(line + '\n参数不足')
            time_txt, liver = args[0], args[1]

            # site 与 title 可省略
            site, title = '', ''
            if len(args) > 2:
                if args[2] in sites:
                    site = args[2]
                    if len(args) == 4:
                        title = args[-1]
                else:
                    title = args[-1]
            if site == '':
                site = 'YouTube'
            if title == '':
                title = liver + ' 转播'
            
            if len(time_txt) != 4:
                raise Exception(line+'\n时间长度不正确')
            try:
                h = int(time_txt[0:-2])
                m = int(time_txt[2:])
            except Exception as e:
                raise Exception(line+'\n无法转换为整数\n'+str(e))
            if h < 0 or h > 24 or m < 0 or m > 60:
                raise Exception(line+'\n时间不在可用范围内')
            
            now = datetime.now(JST)
            time = datetime(now.year, now.month, now.day, h, m,tzinfo=JST)
            if time < now:
                time += timedelta(days=+1)
            lives.append(
                {
                    'time': time,
                    'id': time_txt + liver,
                    'args':{
                        'time': time,
                        'liver':liver,
                        'site': site,
                        'title': title,
                    }
                }
            )
        except Exception as e:
            txt = ''
            if len(str(e).strip()) == 0:
                txt = '\n'+tracemsg(e)
            errmsg('schedule', str(e)+txt)
    return lives


def __make_schedule_post_txt(lives):
    '''读取lives列表，输出用于发动态的时间表字符串
    '''
    txt = '今日转播：\n'
    for live in lives:
        txt += '{}, {}, {}\n{}\n'.format(
            live['time'].strftime(r'%m.%d %H:%M'),
            live['args']['liver'],
            live['args']['site'],
            live['args']['title']
        )
    return txt


def makeLives(CONFIG_PATH):
    '''读取schedule.txt，解析，发送B站动态，并输出直播信息列表

    Args:
        CONFIG_PATH: str, config.ini路径
    
    Returns:
        lives: 直播信息列表，结构如下：
            [
                {
                    'time': datetime.datetime, 用于任务开始的时间，即直播开始的时间
                    'id': str, 用于scheduler中直播任务的唯一id，以 time_txt+liver 的形式保证唯一性
                    'args': {
                        'time': datetime.datetime, 直播开始的时间，与上面的'time'值相同
                        'liver': str, 直播liver名，应在liveInfo.json中存在
                        'site': str, 目前只支持YouTube
                        'title': str, 用于直播间标题的可变内容
                    }
                },
                {...}
            ]
    '''
    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    SCHEDULE_TXT_PATH = config.get('basic', 'SCHEDULE_TXT_PATH')
    COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')

    # Get live list
    text = ""
    with open(SCHEDULE_TXT_PATH, encoding='utf-8') as file:
        text = file.read()
    lives = __analyse_live_list(text)
    lives.sort(key=lambda live:live['time'])

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
    
    return lives