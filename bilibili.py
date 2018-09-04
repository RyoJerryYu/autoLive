import base64
import json
import re
import sys
import time

import requests


class Bilibili:
    def __init__(self):
        self.session = requests.session()
        self.csrf = None

    def login(self, username, password):
        """
        调用第三方API，请谨慎使用
        详情见：http://docs.kaaass.net/showdoc/web/#/2?page_id=3
        :param username:登录的用户名
        :param password:密码
        :return:
        """
        req = self.post(
            url='https://api.kaaass.net/biliapi/user/login',
            data={
                'user': username,
                'passwd': password
            }
        )
        if req['status'] == 'OK':
            login = self.get(
                url='https://api.kaaass.net/biliapi/user/sso',
                params={
                    'access_key': req['access_key']
                }
            )
            if login['status'] == 'OK':
                print(login['cookie'])
                cookies = {}
                for line in login['cookie'].split(';')[:-1]:
                    name, value = line.strip().split('=')
                    cookies[name] = value
                cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
                self.session.cookies = cookies
                self.csrf = self.session.cookies.get('bili_jct')
                return True
            else:
                return login

    def login_by_cookies(self, path):
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
        req = self.get('https://api.vc.bilibili.com/feed/v1/feed/get_attention_list')
        code = req['code']
        if code == 0:
            print("[提示]登录成功！")
            return True
        else:
            print("[提示]cookies失效！")
            print("[提示]登录返回信息为：" + req)
            sys.exit(1)
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
        print(req)

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