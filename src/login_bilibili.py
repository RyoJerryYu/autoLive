import os

from src.methods.m_bilibili import Bilibili
from src.utitls import logmsg, errmsg


def login_bilibili(path):
    b = Bilibili()
    logmsg('尝试通过Cookies登陆Bilibili')
    LOGIN_STATUS = False
    if os.path.exists(path):
        b.login_by_cookies(path)
        if b.isLogin():
            LOGIN_STATUS = True
    else:
        errmsg('login', '找不到cookies.txt')
    if LOGIN_STATUS == False:
        raise Exception('Cookies登陆Bilibili失败')
    my_info = b.get_my_basic_info()
    logmsg("[已登录账号{}][mid:{}][昵称:{}]".format(my_info['userid'], my_info['mid'], my_info['uname']))
    return b