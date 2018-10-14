from datetime import datetime
import json
import os
import traceback
import subprocess


def errmsg(errtype='normal', msg=""):
    textform={
        'normal': '[错误]{time}\n{message}\n',
        'schedule': '[错误]{time}: schedule.txt不符合格式\n{message}\n',
        'login': '[错误]{time}: bilibili登陆失败\n{message}\n',
        'json': '[错误]{time}: json读写错误\n{message}\n',
        'm3u8': '[错误]{time}: m3u8获取失败\n{message}\n',
        'cmd': '[错误]{time}: 调用进程失败\n{message}\n'
    }
    msg = '\n  '.join(msg.split('\n'))
    msg = '  ' + msg
    text = textform[errtype].format(time=datetime.now(), message=msg)
    with open('err.log', 'a', encoding='utf-8') as err:
        err.write(text)
    with open('log.txt', 'a', encoding='utf-8') as log:
        log.write(text)
    print(text)


def logmsg(msg=""):
    textform = '[记录]{time}\n{message}\n'
    msg = '\n  '.join(msg.split('\n'))
    msg = '  ' + msg
    text = textform.format(time=datetime.now(), message=msg)
    with open('log.txt', 'a', encoding='utf-8') as log:
        log.write(text)
    print(text)


def tracemsg(e):
    txt = ''
    for line in traceback.format_tb(e.__traceback__):
        txt += line
    return txt


def dumpJson(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logmsg('写入json文件\n'+path)


def loadJson(path):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    else:
        errmsg('json', path+'\n文件读入错误')
        return -1


def RunCMD(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pid = p.pid
    logmsg('CMD进程开始: PID = {PID}\nCMD:"{CMD}"'.format(PID=pid, CMD=cmd))
    out, err = p.communicate()
    errcode = p.returncode
    logmsg('CMD进程结束: PID = {PID}\nCMD:"{CMD}"\nERR:{ERR}\nCODE:{CODE}'.format(
        PID=pid, CMD=cmd,
        ERR=err, CODE=errcode
    ))
    return out, err, errcode
