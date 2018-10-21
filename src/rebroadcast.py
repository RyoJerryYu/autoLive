# -*- coding: utf-8 -*-
import os
from time import sleep

from src.methods.m_bilibili import Bilibili
from src.methods import m_youtube
from src.login_bilibili import login_bilibili
from src.utitls import logmsg, errmsg, loadJson, tracemsg
from src.Configs import CONFIGs


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
    '''获取转播的网站，返回对应网站中获取m3u8与推流的方法
    '''
    if site == 'YouTube':
        get_m3u8 = m_youtube.get_m3u8
        push_stream = m_youtube.push_stream
    return get_m3u8, push_stream


def rebroadcast(live):
    """一次转播任务的主函数

    一次转播任务分两个阶段
    初始化：
        登陆bilibili
        从liveInfo.json中查得直播间地址
        并获得直播网站的对应get_m3u8与push_stream函数

        此时出现任何异常都会推出rebroadcast函数

    每分钟一次，共20次循环：
        获取m3u8地址
        开启bilibili直播间
        发送开播动态（仅一次）
        开始推流

        为了liver推迟开播、直播中途断开等容错
        此时出现任何异常都会立即继续下一次循环
        其中开播动态只会在第一次成功开始推流前发送一次


    Args:
        args: dict, 结构如下
            {
                'time': datetime.datetime, 
                'liver': string,
                'site': string, default='YouTube',
                'title': string, default='liver+'转播',
            }
        CONFIG_PATH: str, config.ini的路径
    """
    args = live.args()
    try:
        logmsg('开始推流项目：\n{liver}:{site}'.format(liver=args['liver'], site=args['site']))

        # Read Config
        config = CONFIGs()
        COOKIES_TXT_PATH = config.COOKIES_TXT_PATH
        LIVE_INFO_PATH = config.LIVE_INFO_PATH
        BILIBILI_ROOM_TITLE = config.BILIBILI_ROOM_TITLE
        FFMPEG_COMMAND = config.FFMPEG_COMMAND
        BILIBILI_ROOM_AREA_ID = config.BILIBILI_ROOM_AREA_ID
        LIVE_QUALITY = config.LIVE_QUALITY

        b = login_bilibili(COOKIES_TXT_PATH)
        live_url = get_live_url(LIVE_INFO_PATH, args['liver'], args['site'])
        get_m3u8, push_stream = get_method(args['site'])
        
        retry_count = 0
        has_posted_dynamic = False
        while retry_count <= 20:
            try:
                url_m3u8 = get_m3u8(live_url, LIVE_QUALITY)

                room_id = b.getMyRoomId()

                # 防止前一次直播未结束，先暂存旧直播标题，推流错误时将标题重新改回
                old_title = b.getRoomTitle(room_id)

                b.updateRoomTitle(room_id, BILIBILI_ROOM_TITLE.format(
                    time=args['time'],
                    liver=args['liver'],
                    site=args['site'],
                    title=args['title']
                ))
                url_rtmp = b.startLive(room_id, BILIBILI_ROOM_AREA_ID)
                logmsg("开播成功,获得推流地址:{}".format(url_rtmp))
                sleep(5)
                
                # 每次直播只发送一次动态
                if not has_posted_dynamic:
                    dynamic_id = b.send_dynamic(
                        '开始转播：{liver}\n时间：{time}\n{title}\n{url}'.format(
                            liver=args['liver'],
                            time=args['time'].strftime(r'%m.%d %H:%M'),
                            title=args['title'],
                            url='https://live.bilibili.com/'+str(room_id)
                        )
                    )
                    has_posted_dynamic = True
                out, err, errcode = push_stream(url_rtmp, live_url, url_m3u8, FFMPEG_COMMAND)

                # 前一次直播未结束
                if errcode == 1:
                    sleep(10)
                    b.updateRoomTitle(room_id, old_title)
                    sleep(60)
                    raise Exception('直播间被占用')

            except Exception as e:
                msg = tracemsg(e) if len(str(e).strip()) == 0 else str(e)
                errmsg('normal', '项目:{time} {liver}\n尝试推流失败，retry_count={retry_count}\n'.format(
                    time=args['time'], liver=args['liver'], retry_count=retry_count
                ) + msg)
            
            retry_count += 1
            sleep(60)
        
        # 关闭项目前删除已发送的动态
        # 若未发送动态则一定未转播成功

        # 但已发送动态不一定转播成功，可能是由于前一次转播未结束导致
        # 此BUG以后再调整
        if has_posted_dynamic:
            b.delete_dynamic(dynamic_id)
        else:
            b.send_dynamic(
                '转播失败: {liver}, {site}\n时间: {time}\n{title}'.format(
                    liver=args['liver'],
                    time=args['time'],
                    title=args['title'],
                    site=args['site']
                )
            )

    except Exception as e:
        txt = ''
        if len(str(e).strip()) == 0:
            txt = '\n'+tracemsg(e)
        errmsg('schedule', str(e)+txt)
        
    logmsg('关闭推流项目：\n{liver}:{site}'.format(liver=args['liver'], site=args['site']))