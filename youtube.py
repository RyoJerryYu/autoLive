import configparser
import os
import re
import sys
import time
from datetime import datetime
from bilibili import Bilibili
# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')
BILIBILI_ROOM_TITLE = config.get('live', 'BILIBILI_ROOM_TITLE')
FFMPEG_COMMAND = config.get('live', 'FFMPEG_COMMAND')
ALWAYS_USE_HIGHEST_QUALITY = config.getboolean('youtube-dl', 'ALWAYS_USE_HIGHEST_QUALITY')
BILIBILI_ROOM_AREA_ID = config.getint('live', 'BILIBILI_ROOM_AREA_ID')


if __name__ == '__main__':
    LOGIN_STATUS = False
    print("[提示]Youtube转播工具v1.0")
    b = Bilibili()
    if os.path.exists(COOKIES_TXT_PATH):  # 自动登录
        print("[提示]找到cookies.txt,尝试自动登录...")
        b.login_by_cookies(COOKIES_TXT_PATH)
        if b.isLogin():
            LOGIN_STATUS = True
    if not LOGIN_STATUS:
        login_type = input("[提示]请选择Bilibili登录方式:\n1.cookies登录\n2.账号密码登录(不推荐)\n(程序启动会自动读取同级目录下的cookies.txt文件尝试登录,如果登录成功,则自动跳过这一步)\n请选择:")
        if login_type == '1':
            cookies = input("[提示]请粘贴cookies信息:")
            b.login_by_cookies_str(cookies)
            b.isLogin()
        elif login_type == '2':
            username = input("[提示]请输入用户名:")
            password = input("[提示]请输入密码:")
            b.login(username, password)
            b.isLogin()
        else:
            print("[提示]你说什么啊,我听不懂~")
            print("BOOM!")
            sys.exit()
    my_info = b.get_my_basic_info()
    print("[提示][已登录账号{}][mid:{}][昵称:{}]".format(my_info['userid'], my_info['mid'], my_info['uname']))
    print("[提示]请输入Youtube直播地址:")
    print("[提示]格式1.https://www.youtube.com/watch?v=xXxxXxxxXxx")
    print("[提示]格式2.https://www.youtube.com/channel/UCxxxxXXxXXXXXXxxxxXXXx/live")
    print("[提示]格式3.https://youtu.be/XxxxXXXxxxX")
    youtube_live_url = input("请输入:")
    f = os.popen('youtube-dl -F {} --no-check-certificate'.format(youtube_live_url))
    codes = []
    ana = f.read().strip()
    print(ana)
    for line in ana.split('\n'):
        code = re.findall('(\\d+)', line[:5])
        if len(code) != 0:
            codes.append(int(code[0]))
    codes.sort()
    if not ALWAYS_USE_HIGHEST_QUALITY:  # 自动选择清晰度
        quality_code = int(input("[提示]请选择推流清晰度,只可在{}中选择:\n".format(codes)))
        while True:
            if quality_code not in codes:
                print("[提示]请输入正确的清晰度代码")
                quality_code = int(input("[提示]请选择推流清晰度,只可在{}中选择:\n".format(codes)))
            else:
                break
        print("[提示]获得指定清晰度的m3u8地址...")
    else:
        quality_code = codes[-1]
        print("[提示]自动获得最高清晰度的m3u8地址...")
    while True:
        try:
            f = os.popen('youtube-dl -f {} -g {} --no-check-certificate'.format(quality_code, youtube_live_url))
            m3u8_url = f.read().strip()
            print(len(m3u8_url))
            print("[提示]获得直播源m3u8地址:" + m3u8_url)
            room_id = b.getMyRoomId()
            b.updateRoomTitle(room_id, BILIBILI_ROOM_TITLE)
            rtmp_code = b.startLive(room_id, BILIBILI_ROOM_AREA_ID)
            print("[提示]开播成功,获得推流地址:{}".format(rtmp_code[:49]+"□□□□□□□□□□这里打个码□□□□□□□□□□"))
            print("这里停一停让观众看清楚")
            time.sleep(5)
            command = FFMPEG_COMMAND.format(m3u8_url, rtmp_code)
            os.system(command)
        except Exception as e:
            with open("log.txt", "a") as log:
                log.write("{}发生错误,错误信息:{}".format(datetime.now(), e))


