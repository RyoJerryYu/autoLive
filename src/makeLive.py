import os
from datetime import datetime, timedelta, timezone
import configparser

from utitls import errmsg, tracemsg, logmsg
from src.login_bilibili import login_bilibili


def __analyse_live_list(text):
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