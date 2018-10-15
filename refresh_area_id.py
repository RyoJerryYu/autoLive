# -*- coding: utf-8 -*-
'''refresh_area_id.py
登陆Bilibili，读取直播分区信息，并更新area_id.txt。
需要Bilibili类，并cookies.txt中已填好可登陆的cookie。
代码未封装到函数中，不建议在其他代码中导入。
'''

from datetime import datetime

from src.methods.m_bilibili import Bilibili


txt = '最终修改于：{time}\n\n'.format(time=datetime.now().strftime(r'%Y %m.%d %H:%M'))
b = Bilibili()
b.login_by_cookies('cookies.txt')
if b.isLogin():
    getLiveAreaListReq=b.get(
            url='https://api.live.bilibili.com/room/v1/Area/getList',
            params={'show_pinyin': 1}
        )['data']
    getLiveAreaListReq.sort(key=lambda zone:zone['id'])
    for zone in getLiveAreaListReq:
        txt += '{id}.{name}\n'.format(id=zone['id'], name=zone['name'])
        zone['list'].sort(key=lambda area:area['id'])
        for area in zone['list']:
            if area['lock_status'] == '0':
                txt += '    {id}.{name}\n'.format(id=area['id'], name=area['name'])

print(txt)
with open('area_id.txt','w', encoding='utf-8') as f:
    f.write(txt)
