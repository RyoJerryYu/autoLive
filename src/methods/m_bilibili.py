#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import re
import sys
import time

import requests


class Bilibili:
    '''登陆、开始直播、发动态等与bilibili交互的类。

    大部分未经修改引用自https://github.com/7rikka/autoLive
    并添加了少部分函数

    Attributes:
        session: requests.session()
        csrf: B站账户验证时需的字符串，来自cookie中的bili-jct。
    '''
    def __init__(self):
        self.session = requests.session()
        self.csrf = None

    def login_by_cookies(self, path):
        '''读取cookies文件并设置cookies

        Args:
            path: cookies.txt文件的路径
        '''
        try:
            with open(path, 'r') as f:
                cookies = {}
                for line in f.read().split(';'):
                    name, value = line.strip().split('=', 1)
                    cookies[name] = value
                cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
                self.session.cookies = cookies
                self.csrf = self.session.cookies.get('bili_jct')
                print("[提示]Cookies设置成功")
        except:
            print("[提示]设定cookies失败,请检查是否写入正确的cookies信息")

    def login_by_cookies_str(self, cookies_str):
        '''直接通过cookies字符串登陆
        '''
        try:
            cookies = {}
            for line in cookies_str.split(';'):
                name, value = line.strip().split('=', 1)
                cookies[name] = value
            cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
            self.session.cookies = cookies
            self.csrf = self.session.cookies.get('bili_jct')
            print("Cookies设置成功")
        except Exception as e:
            print("[提示]设定cookies失败,请检查是否写入正确的cookies信息")

    def isLogin(self):
        '''测试cookies能否登陆

        Returns:
            True | False
        '''
        req = self.get('https://api.vc.bilibili.com/feed/v1/feed/get_attention_list')
        code = req['code']
        if code == 0:
            print("[提示]登录成功！")
            return True
        else:
            print("[提示]cookies失效！")
            print("[提示]登录返回信息为：" + str(req))
            return False
    
    def post(self, url, data, headers=None, params=None):
        while True:
            try:
                if headers is None:
                    if params is None:
                        req = self.session.post(url, data=data,timeout=99999)
                    else:
                        req = self.session.post(url, data=data, params=params,timeout=99999)
                else:
                    if params is None:
                        req = self.session.post(url, data=data, headers=headers,timeout=99999)
                    else:
                        req = self.session.post(url, data=data, headers=headers, params=params,timeout=99999)
                        # print(req.url)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print("[POST][提示]JSON化失败:"+str(e)+"\n[提示]内容为:"+req.text)
                        return req.text
                else:
                    print("[提示]状态码为"+str(req.status_code)+"！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]POST出错\n[提示]%s" % str(e))

    def get(self, url, params=None, headers=None):
        while True:
            try:
                if params is None:
                    if headers is None:
                        req = self.session.get(url, timeout=5)
                    else:
                        req = self.session.get(url, headers=headers, timeout=5)
                else:
                    if headers is None:
                        req = self.session.get(url, params=params, timeout=5)
                    else:
                        req = self.session.get(url, params=params, headers=headers, timeout=5)
                if req.status_code == 200:
                    try:
                        # print(req.text)
                        req.encoding = req.apparent_encoding
                        return req.json()
                    except Exception as e:
                        # print("[GET][提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.content.decode('utf-8')
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    # sys.exit(0)
                    time.sleep(1)
            except Exception as e:
                print("[提示]GET出错\n[提示]%s" % str(e))

    def getMyChooseArea(self, mid):
        """
        查询我的直播间最近使用过的分类
        :param mid:直播间id
        :return:
        """
        req = self.get(
            url='https://api.live.bilibili.com/room/v1/Area/getMyChooseArea',
            params={'roomid':mid}
        )
        print(req)
        if req['code'] == 0:
            return req['data']

    def getLiveAreaList(self, show_pinyin=1):
        """
        获得直播分类信息
        :param show_pinyin:
        :return:
        """
        req = self.get(
            url='https://api.live.bilibili.com/room/v1/Area/getList',
            params={'show_pinyin': show_pinyin}
        )
        if req['code'] == 0:
            return req['data']
            

    def startLive(self, room_id, area_id):
        """
        开始直播,获取推流码
        :param room_id: 自己直播间id
        :param area_id: 直播间分区id
        :return:
        """
        req = self.post(
            url='https://api.live.bilibili.com/room/v1/Room/startLive',
            data={
                'room_id': room_id,
                'platform': 'pc',
                'area_v2': area_id,
                'csrf_token': self.csrf
            }
        )
        if req['code'] == 0:
            rtmp_code = req['data']['rtmp']['addr']+req['data']['rtmp']['code']
            new_link = req['data']['rtmp']['new_link']
            # print("[提示]开播成功,获得推流地址:{}".format(rtmp_code))
            # print("[提示]开播成功,获得new_link:{}".format(new_link))
            return rtmp_code
        else:
            print("[提示]开播出现问题!code={},message={}".format(req['code'],req['message']))

    def stopLive(self, room_id):
        """
        关闭我的直播
        :param room_id: 直播间id
        :return:
        """
        req = self.post(
            url='https://api.live.bilibili.com/room/v1/Room/stopLive',
            data={
                'room_id': room_id,
                'platform': 'pc',
                'csrf_token': self.csrf
            }
        )
        if req['code'] == 0 and req['message'] == '' and req['data']['change'] == 1:
            print("[提示]关播成功!")
        elif req['code'] == 0 and req['message'] == '重复关播' and req['data']['change'] == 0:
            print("[提示]重复关播!请勿重复提交关播请求!")
        else:
            print(req)

    def getMyRoomId(self):
        req = self.get(
            url='https://api.live.bilibili.com/i/api/liveinfo'
        )
        # print(req)
        if req['code'] == 0:
            print("[提示]获得直播间id为[{}]".format(req['data']['roomid']))
            return req['data']['roomid']
        else:
            print("[提示]无法获得直播间id")
    
    def getRoomTitle(self, room_id):
        req = self.get(
            url='https://api.live.bilibili.com/room/v1/Room/get_info',
            params={
                'room_id': room_id,
                'from': 'room'
            }
        )
        if req['code'] == 0:
            print("[提示]获得直播间标题为[{}]".format(req['data']['title']))
            return req['data']['title']

    def updateRoomTitle(self, room_id, title):
        req = self.post(
            url='https://api.live.bilibili.com/room/v1/Room/update',
            data={
                'room_id': room_id,
                'title': title,
                'csrf_token': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]直播间{}标题已更新为:{}".format(room_id, title))
        else:
            print("[提示]修改失败!返回信息为:{}".format(req))

    def get_my_basic_info(self):
        """
        获得此账号的基本信息(个人中心-我的信息)
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/account',

        )
        if req['code'] == 0:
            return req['data']
    
    def send_dynamic(self, content):
        '''发送动态

        post访问http://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost
        发送Bilibili动态

        Args:
            content: str, 动态的内容
        
        Returns:
            req['data']['dynamic_id']: post请求返回的动态id。
            req['data']如下:
            
            {
                'result': 0,
                'errmsg': '符合条件，允许发布',
                'dynamic_id': xxxxxxxxxxxx(int),
                'create_result': 1,
                '_gt_': 0
            }
        '''
        req = self.post(
            url='http://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/repost',
            data={
                'dynamic_id': '0',
                'type': '4',
                'rid': '0',
                'content': content.replace(r'\n', '\n'),
                'at_uids': '',
                'ctrl': '[]',
                'csrf_token': self.csrf
            }
        )
        if req['code'] == 0:
            return req['data']['dynamic_id']
    
    def delete_dynamic(self, dynamic_id):
        '''删除动态

        :param int dynamic_id: 所删除动态的id
        '''
        uid = self.get_my_basic_info()['mid']
        req = self.post(
            url='https://api.vc.bilibili.com/dynamic_repost/v1/dynamic_repost/rm_rp_dyn',
            data={
                'uid': uid,
                'dynamic_id': dynamic_id,
                'csrf_token': self.csrf
            }
        )
        if req['code'] == 0:
            return req['data']