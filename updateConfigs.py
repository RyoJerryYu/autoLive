# -*- coding: utf-8 -*-
from configparser import ConfigParser


def SetupConfigs():
    COOKIE_FAILED = False
    PORT_FAILED = False
    try:
        print('###############################')
        print('#                             #')
        print('# paste your bilibili cookies #')
        print('#                             #')
        print('###############################')
        print('粘贴B站cookies。注意不要把开头的“Cookie:”也一起复制。')
        print('如果此处写入失败，请手动把Cookie写入cookies.txt')
        cookies = input('粘贴cookies到此处:')
        with open('cookies.txt', 'w', encoding='utf-8') as f:
            f.write(cookies)
    except:
        print('cookies写入失败，请手动写入cookies.txt')
        COOKIE_FAILED = True
    try:
        new_configs = ConfigParser()
        new_configs.read('config.ini', encoding='utf-8')
        print('请输入打算使用的端口号，必须是0~65535之间的一个数字，并避开80、22等常用端口。')
        print('如果此处设置不成功，也可在config.ini设置')
        port = input('请输入端口号(推荐输入2434)：')
        port = int(port)
        if port < 0 or 65535 < port:
            raise Exception
        new_configs.set('basic', 'WEB_PORT', str(port))
        new_configs.write(open('config.ini', 'w', encoding='utf-8'))
    except:
        print('端口号设置失败，请手动从config.ini设置。')
        PORT_FAILED = True
    
    print('###############################')
    print('从ver2.1.0起一键安装脚本不再自动启动程序。')
    print('请手动按以下步骤启动。')
    print('1. 输入命令：')
    print('screen -S autoLive # 打开新的screen窗口并命名为autoLive。在screen中启动的程序即使关闭shell也能继续运行。')
    print('2. 输入命令：')
    print('cd ~/autoLive # 进入autoLive文件夹。本程序必须从autoLive文件夹中打开。')
    print('3. 输入命令：')
    print('python36 main.py # 使用python3.6运行本程序。')
    print('4. 程序运行后，按ctrl+A后，按下d键退出screen窗口。')
    print('此时在screen中启动的程序仍会在后台运行。')
    print('可以从浏览器访问http://<服务器ip>:<端口>/autoLive，如果出现界面正常则程序运行成功。')
    print('######')
    print('停止程序时请按以下步骤停止。')
    print('1. 输入命令：')
    print('screen -r autoLive # 恢复名为autoLive的screen窗口')
    print('2. 按下ctrl+C停止程序，可能需要多按几次。')
    print('3. 输入命令：')
    print('exit # 退出并关闭screen窗口。')
    print('#############################')
    print('安装终了！')
    if COOKIE_FAILED:
        print('cookies写入失败，请手动写入cookies.txt')
    if PORT_FAILED:
        print('端口号设置失败，请手动从config.ini设置。')

if __name__ == '__main__':
    SetupConfigs()