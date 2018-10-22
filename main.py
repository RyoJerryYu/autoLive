#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

from src.liveScheduler import LiveScheduler
from src.utitls import errmsg, logmsg, tracemsg
from src.makeLive import makeLives, post_schedule
from src.rebroadcast import rebroadcast
from src.Configs import CONFIGs
from src.webSite import web


def main(CONFIG_PATH):
    '''程序主入口
    
    调用makeLives获得live列表，添加到scheduler后启动scheduler。

    Args:
        CONFIG_PATH: str, config.ini的储存位置。
    '''
    # CONFIG初始化，必须放在所有步骤前
    configs = CONFIGs()
    configs.set_configs(CONFIG_PATH)

    logmsg('程序启动')

    # 解析schedule.txt并发送每日转播表动态
    lives = makeLives()
    post_schedule(lives)

    # LiveScheduler为单例类，初始化需在web运行前
    scheduler = LiveScheduler()
    for live in lives:
        scheduler.add_live(rebroadcast, live)
    
    try:
        scheduler.start()
        logmsg('时间表启动')

        # APScheduler直接调用shutdown不会等待未开始执行的任务
        # get_jobs返回空列表时所有任务都已开始执行
        # 此时调用shutdown才会等待已开始执行的任务结束
        # while len(scheduler.get_jobs()) != 0:
        #     sleep(600)

        web.run()

        scheduler.shutdown()
    except KeyboardInterrupt:
        errmsg('normal', '因KeyboardInterrupt退出')
    except Exception as e:
        msg = str(e) +'\n' + tracemsg(e)
        errmsg('normal', msg)
    
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logmsg('程序结束')


if __name__ == '__main__':
    main('config.ini')