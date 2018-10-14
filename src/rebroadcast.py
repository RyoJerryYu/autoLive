import configparser
import os
from time import sleep

from src.methods.m_bilibili import Bilibili
from src.methods import m_youtube
from src.login_bilibili import login_bilibili
from src.utitls import logmsg, errmsg, loadJson, tracemsg


def get_live_url(path, liver, site='YouTube'):
    lives_info = loadJson(path)
    live_url = ''
    for live_info in lives_info:
        if live_info['liver'] == liver:
            for room in live_info['room']:
                if room['site'] == site:
                    live_url = room['url']
    if len(live_url) == 0:
        raise Exception(path+'\n文件中找不到直播url地址')
    logmsg('获得直播url地址：'+live_url)
    return live_url


def get_method(site='YouTube'):
    if site == 'YouTube':
        get_m3u8 = m_youtube.get_m3u8
        push_stream = m_youtube.push_stream
    return get_m3u8, push_stream


def rebroadcast(args, CONFIG_PATH):
    """
    :param args:{
        'time': datetime.datetime, 
        'liver': string,
        'site': string, default='YouTube',
        'title': string, default='liver+'转播',
    }
    """
    try:
        logmsg('开始推流项目：\n{liver}:{site}'.format(liver=args['liver'], site=args['site']))

        # Read Config
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH, encoding='utf-8')
        COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')
        LIVE_INFO_PATH = config.get('basic', 'LIVE_INFO_PATH')
        BILIBILI_ROOM_TITLE = config.get('live', 'BILIBILI_ROOM_TITLE')
        FFMPEG_COMMAND = config.get('live', 'FFMPEG_COMMAND')
        BILIBILI_ROOM_AREA_ID = config.getint('live', 'BILIBILI_ROOM_AREA_ID')
        LIVE_QUALITY = config.getint('youtube-dl', 'LIVE_QUALITY')

        b = login_bilibili(COOKIES_TXT_PATH)
        live_url = get_live_url(LIVE_INFO_PATH, args['liver'], args['site'])
        get_m3u8, push_stream = get_method(args['site'])
        
        retry_count = 0
        has_posted_dynamic = False
        while retry_count <= 20:
            try:
                url_m3u8 = get_m3u8(live_url, LIVE_QUALITY)

                room_id = b.getMyRoomId()
                b.updateRoomTitle(room_id, BILIBILI_ROOM_TITLE.format(
                    time=args['time'],
                    liver=args['liver'],
                    site=args['site'],
                    title=args['title']
                ))
                url_rtmp = b.startLive(room_id, BILIBILI_ROOM_AREA_ID)
                logmsg("开播成功,获得推流地址:{}".format(url_rtmp))
                sleep(5)
                
                # run
                if not has_posted_dynamic:
                    b.send_dynamic(
                        '开始转播：{liver}\n时间：{time}\n{title}'.format(
                            liver=args['liver'],
                            time=args['time'].strftime(r'%m.%d %H:%M'),
                            title=args['title']
                        )
                    )
                    has_posted_dynamic = True
                push_stream(url_rtmp, live_url, url_m3u8, FFMPEG_COMMAND)

            except Exception as e:
                msg = str(e) + '\n' + tracemsg(e)
                errmsg('normal', '项目:{time} {liver}\n尝试推流失败，retry_count={retry_count}\n'.format(
                    time=args['time'], liver=args['liver'], retry_count=retry_count
                ) + msg)
            
            retry_count += 1
            sleep(60)

    except Exception as e:
        txt = ''
        if len(str(e).strip()) == 0:
            txt = '\n'+tracemsg(e)
        errmsg('schedule', str(e)+txt)
        
    logmsg('关闭推流项目：\n{liver}:{site}'.format(liver=args['liver'], site=args['site']))