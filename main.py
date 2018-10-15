#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
from datetime import datetime
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler

from src.utitls import errmsg, logmsg, tracemsg
from src.makeLive import makeLives
from src.rebroadcast import rebroadcast


def main(CONFIG_PATH):
    '''程序主入口
    
    调用makeLives获得live列表，添加到scheduler后启动scheduler。

    Args:
        CONFIG_PATH: str, config.ini的储存位置。
    '''
    # Read config
    logmsg('程序启动')
    lives = makeLives(CONFIG_PATH)
    scheduler = BackgroundScheduler()
    for live in lives:
        scheduler.add_job(rebroadcast, trigger='date', run_date=live['time'], args=[live['args'], CONFIG_PATH], id=live['id'])
    try:
        scheduler.start()
        while len(scheduler.get_jobs()) != 0:
            sleep(600)
        scheduler.shutdown()
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)
        errmsg('normal', '因KeyboardInterrupt退出')
    except Exception as e:
        msg = str(e) +'\n' + tracemsg(e)
        errmsg('normal', msg)
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logmsg('程序结束')


if __name__ == '__main__':
    main('config.ini')