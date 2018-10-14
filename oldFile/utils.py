import re

import requests

"""
说明
(1)channel_id 频道名称类似于链接https://www.twitch.tv/shroud,shroud即为频道名称
(2)vod,直播录像id,类似于链接https://www.twitch.tv/videos/303763956,303763956即为录像id
(3)get_channel_live_m3u8默认返回chunked画质(即为原画质)的m3u8链接
"""


def get_channel_live_m3u8(channel_id):
    """
    获得频道直播的m3u8
    :param channel_id:
    :return:
    """
    client_id = '4zswqk0crwt2wy4b76aaltk2z02m67'
    print("[提示]当前使用CLIENT_ID:{}".format(client_id))
    req = requests.get(
        url='https://api.twitch.tv/api/channels/{}/access_token'.format(channel_id),
        params={'client_id': client_id}

    )
    # print(req)
    sig = req.json()['sig']
    token = req.json()['token']
    print("[提示]获得signature:{},获得token:{}".format(token, sig))
    req = requests.get(url='https://usher.ttvnw.net/api/channel/hls/{}.m3u8'.format(channel_id),
                       params={
                           'allow_source': 'true',
                           'nauth': token,
                           'nauthsig': sig,
                       })
    print(req.text)
    videolist = []
    besturl = ''
    lines = req.text.split('\n')
    for i in range(2, len(lines)-1, 3):
        info = re.findall('BANDWIDTH=(\\d+),RESOLUTION=(.*?),CODECS="(.*?)",VIDEO="(.*?)"', lines[i+1])[0]
        # print(lines[i+1])
        if info[3] == 'chunked':
            besturl = lines[i+2]
            videolist.append({
                "best": lines[i+2]
            })
        videolist.append({
            'bandwidth': info[0],
            'codecs': info[2],
            'resolution': info[1],
            'video': info[3],
            'url': lines[i+2]
        })
    return besturl


def get_vod_m3u8(vod):
    """
    获得直播录像的m3u8
    :param vod:
    :return:
    """
    client_id = '4zswqk0crwt2wy4b76aaltk2z02m67'
    print("[提示]使用CLIENT_ID:{}解析VOD:{}".format(client_id, vod))
    req = requests.get(
        url='https://api.twitch.tv/api/vods/{}/access_token'.format(vod),
        params={'client_id': client_id}
    )
    sig = req.json()['sig']
    token = req.json()['token']
    print("[提示]获得signature:{},获得token:{}".format(token, sig))
    print("[提示]获取VOD:{}的m3u8地址...".format(vod))
    req = requests.get(
        url='https://usher.ttvnw.net/vod/{}.m3u8'.format(vod),
        params={
            'allow_source': 'true',
            'nauth': token,
            'nauthsig': sig,
        })
    videolist = []
    besturl = ''
    lines = req.text.split('\n')
    for i in range(2, len(lines)-1, 3):
        info = re.findall('BANDWIDTH=(\\d+),CODECS="(.*?)",RESOLUTION="(.*?)",VIDEO="(.*?)"', lines[i+1])[0]
        if info[3] == 'chunked':
            besturl = lines[i+2]
            videolist.append({
                "best": lines[i+2]
            })
        videolist.append({
            'bandwidth': info[0],
            'codecs': info[1],
            'resolution': info[2],
            'video': info[3],
            'url': lines[i+2]
        })
    return besturl