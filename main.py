#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

from src.liveScheduler import LiveScheduler
from src.utitls import errmsg, logmsg, tracemsg
from src.makeLive import makeLives, post_schedule
from src.rebroadcast import rebroadcast
from src.Configs import CONFIGs


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

    lives = makeLives()
    post_schedule(lives)

    scheduler = LiveScheduler()
    for live in lives:
        scheduler.add_live(rebroadcast, live)
    
    try:
        scheduler.start()
        while len(scheduler.get_jobs()) != 0:
            sleep(600)
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