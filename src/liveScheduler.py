from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
from datetime import datetime, timedelta, timezone

from src.utitls import sigleton, errmsg, tracemsg, logmsg
from src.Configs import CONFIGs
from src.login_bilibili import login_bilibili


@sigleton
class LiveScheduler(BackgroundScheduler):
    '''直播定时任务

    单例类，保证不同模块中可使用同一个实例

    Members:
        __scheduler: BackgroundScheduler
        __lives: dict, key为live.id(), value为对应的live类
        __livings: dict, key与value同上，保存正在进行中的live类

    Methods:
        add_live, get_lives, get_live, remove_live, post_schedule
    '''
    def __init__(self, *args, **kw):
        '''构造函数

        构造实例时会添加自动发送每日动态的任务
        每日本地时间15时时发送每日动态
        由于是单例类，所以此任务不会重复添加
        '''
        self.__lives = {}
        self.__livings = {}
        super().__init__(*args, **kw)
        
        # 此处post_schedule使用本地时区
        # APScheduler中使用时区只支持pytz
        self.add_job(
            self.post_schedule,
            trigger='cron',
            hour=15
        )
    
    def __exefunc_decorator(self, func):
        '''执行函数装饰器

        用于装饰live执行函数
        使调用前将live移出__lives并加入__livings
        调用后移出__livings
        在add_live内部调用
        不改变原函数定义

        :param func: live执行函数, 参数应为(live, *args)
        :return wrapper:
        '''
        @wraps(func)
        def wrapper(live, *args):
            live_id = live.live_id()
            self.__lives.pop(live_id)
            self.__livings[live_id] = {
                'live': live,
                'startT': datetime.now()
            }
            func(live, *args)
            self.__livings.pop(live_id)
        return wrapper
    
    def add_live(self, func, live, *args):
        '''添加live项目进入时间表

        把live用对应格式加入scheduler
        并加入live列表后返回对应live的live_id

        live_id是时间表中live的唯一标记
        可用于pop_live与get_live函数

        :param func: 执行转播的函数
        :param live: live类，直播项目
        :return live_id: 时间表中对应live实例的live_id
        '''
        live_id = live.live_id()
        self.add_job(
            func=self.__exefunc_decorator(func),
            trigger='date',
            run_date=live.time,
            args=[live]+[x for x in args],
            id=live_id
        )
        self.__lives[live_id] = live
        return live_id
    
    def get_lives(self):
        '''获取时间表中的live列表
        '''
        return self.__lives
    
    def get_live(self, live_id):
        '''获取live_id对应的live实例
        '''
        return self.__lives[live_id]
    
    def pop_live(self, live_id):
        '''将live_id对应live移出时间表并返回live实例
        '''
        self.remove_job(live_id)
        live = self.__lives.pop(live_id)
        return live

    def get_livings(self):
        '''获取已运行的live列表
        '''
        return self.__livings
    
    def __make_schedule_post_txt(self, lives):
        '''读取lives列表，输出用于发动态的时间表字符串
        '''
        DAILY_DYNAMIC_FORM = CONFIGs().DAILY_DYNAMIC_FORM
        txt = '今日转播：\n时间均为日本时区\n'
        for live in lives:
            txt += DAILY_DYNAMIC_FORM.format(
                time=live.time.strftime(r'%m.%d %H:%M'),
                liver=live.liver,
                site=live.site,
                title=live.title
            )
        return txt
    
    def post_schedule(self, lives=None):
        '''发送时间表动态

        Args:
            lives: 直播信息列表
        
        Returns:
            0: 正常发送动态
            -1: 发送动态过程中出错
        '''
        # 兼容旧版保留lives参数
        # 如果没有给lives参数则获取时间表中的lives
        if not lives:
            lives = self.__lives.values()
        # Read config
        config = CONFIGs()
        COOKIES_TXT_PATH = config.COOKIES_TXT_PATH
        IS_SEND_DAILY_DYNAMIC = config.IS_SEND_DAILY_DYNAMIC

        # 如果没有直播预定或设置为不发送动态，则中止
        if len(lives) == 0 or not IS_SEND_DAILY_DYNAMIC:
            return 0

        # Post dynamic
        try:
            schedule_post_txt = self.__make_schedule_post_txt(lives)
            b = login_bilibili(COOKIES_TXT_PATH)
            if b.send_dynamic(schedule_post_txt):
                logmsg('发送每日动态成功')
            else:
                errmsg('发送每日动态失败')
                return -1
        except Exception as e:
            txt = ''
            if len(str(e).strip()) == 0:
                txt = '\n'+tracemsg(e)
            errmsg('schedule', str(e)+txt)
            return -1
        return 0
    

class Live:
    '''直播信息

    Members:
        time, datetime.datetime, 直播开始时间
        liver, str, 直播liver名，应在liveInfo.json中存在
        site, str, 目前只支持YouTube
        title, str, 用于直播间标题的可变内容
    '''
    def __init__(self, time, liver, site='', title=''):
        '''Live类构造函数

        site与title参数为与旧格式兼容
        可支持省略或填入空字符串

        :param datetime|str time:可使用datetime实例或长度为4的时间字符串
        :param str liver:
        :param str site: 默认值为'YouTube'
        :param str title: 默认值为liver+' 转播'
        '''
        if isinstance(time, str):
            time = Live.analyse_time_text(time)
        if site == '':
            site = 'YouTube'
        if title == '':
            DEFAULT_TITLE_PARAM = CONFIGs().DEFAULT_TITLE_PARAM
            title = DEFAULT_TITLE_PARAM.format(
                time=time.strftime(r'%m.%d %H:%M'),
                liver=liver,
                site=site
            )
        self.time = time
        self.liver = liver
        self.site = site
        self.title = title
    
    def args(self):
        '''返回rebroadcast的args参数
        '''
        args = {
            'time': self.time,
            'liver': self.liver,
            'site': self.site,
            'title': self.title
        }
        return args
    
    def live_id(self):
        '''返回用于scheduler的job_id
        '''
        live_id = self.time.strftime('%H%M') + self.liver
        return live_id
    
    @staticmethod
    def analyse_time_text(time_txt):
        '''分析四位长度的time_txt并返回符合的datetime实例

        time_txt可接受特殊值："now"
        此外仅能填入长度为4位，格式为HHMM，的24小时制时间
        当得出时间小于当前时，自动调整为第二天

        特殊值：
        now: 返回datetime.now()的30秒后

        :param str time_txt: 四位长度HHMM字符串
        '''
        JST = timezone(timedelta(hours=+9), 'JST')
        assert isinstance(time_txt, str)

        # time_txt填入now参数时
        if time_txt.lower() == 'now':
            time = datetime.now(JST) + timedelta(seconds=+30)
            return time

        # time格式仅能为HHMM，24小时制
        if len(time_txt) != 4:
            raise Exception(time_txt+'\n时间长度不正确')
        try:
            h = int(time_txt[0:-2])
            m = int(time_txt[2:])
        except Exception as e:
            raise Exception(time_txt+'\n无法转换为整数\n'+str(e))
        if h < 0 or h > 24 or m < 0 or m > 60:
            raise Exception(time_txt+'\n时间不在可用范围内')

        # 识别24小时内的第二天
        now = datetime.now(JST)
        time = datetime(now.year, now.month, now.day, h, m,tzinfo=JST)
        if time < now:
            time += timedelta(days=+1)
        return time
    
    @staticmethod
    def livefScheduleTxt(line):
        '''读取一行时间表返回一个live实例

        时间表格式：
        time@liver@site@title
        time: 直播时间，可接收特殊参数"now"。
              此外格式仅能为HHMM，只接受未来24小时内的直播，检测出直播时间在运行程序之前时，会自动认为直播在运行程序第二天开始。
        liver：只接受liveInfo.json中存在的liver名。（可自行按json格式添加到liveInfo文件中）
        site：直播网站，目前只接受YouTube。而且不填默认为YouTube。
        title：填入config.ini中直播间标题的title中，可选，不填默认为"{liver}"+"转播"

        :param str line: 符合格式的时间表中的一行
        '''
        sites = ['YouTube']
        
        args = line.split('@')
        if len(args) < 2:
            raise Exception(line + '\n参数不足')
        time_txt, liver = args[0], args[1]

        # site 与 title 可省略
        site, title = '', ''
        if len(args) > 2:
            if args[2] in sites:
                site = args[2]
                if len(args) > 3:
                    title = args[-1]
            else:
                title = args[-1]
        
        time = Live.analyse_time_text(time_txt)
        return Live(time, liver, site, title)