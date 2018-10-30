from configparser import ConfigParser

from src.utitls import sigleton


@sigleton
class CONFIGs:
    def set_configs(self, path):
        '''CONFIG初始化

        读取路径为path的设定文件
        必须在所有使用到设定的步骤之前
        '''
        config = ConfigParser()
        config.read(path, encoding='utf-8')
        self.__CONFIG_PATH = path

        # 基本设置，不会在设置页面显示
        self.WEB_PORT = config.getint('basic', 'WEB_PORT')
        self.COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')
        self.LIVE_INFO_PATH = config.get('basic', 'LIVE_INFO_PATH')
        self.SCHEDULE_TXT_PATH = config.get('basic', 'SCHEDULE_TXT_PATH')
        self.FFMPEG_COMMAND = config.get('basic', 'FFMPEG_COMMAND')

        # bilibili相关设置
        self.BILIBILI_ROOM_TITLE = config.get('bilibili', 'BILIBILI_ROOM_TITLE')
        self.DEFAULT_TITLE_PARAM = config.get('bilibili', 'DEFAULT_TITLE_PARAM')
        self.BILIBILI_ROOM_AREA_ID = config.getint('bilibili', 'BILIBILI_ROOM_AREA_ID')
        self.IS_SEND_DAILY_DYNAMIC = config.getboolean('bilibili', 'IS_SEND_DAILY_DYNAMIC')
        self.DAILY_DYNAMIC_FORM = config.get('bilibili', 'DAILY_DYNAMIC_FORM')
        self.IS_SEND_PRELIVE_DYNAMIC = config.getboolean('bilibili', 'IS_SEND_PRELIVE_DYNAMIC')
        self.PRELIVE_DYNAMIC_FORM = config.get('bilibili', 'PRELIVE_DYNAMIC_FORM')

        # 直播参数相关设置
        self.LIVE_QUALITY = config.getint('liveParam', 'LIVE_QUALITY')
    
    def save_configs(self):
        '''将实例中设置项成员保存至文件

        更改设置项后应立即运行此函数
        以免程序停止后设置项复原
        '''
        config = ConfigParser()
        config.read(self.__CONFIG_PATH, encoding='utf-8')

        # 基本设置不能在程序中更改

        # bilibili相关设置
        config.set('bilibili', 'BILIBILI_ROOM_TITLE', str(self.BILIBILI_ROOM_TITLE))
        config.set('bilibili', 'DEFAULT_TITLE_PARAM', str(self.DEFAULT_TITLE_PARAM))
        config.set('bilibili', 'BILIBILI_ROOM_AREA_ID', str(self.BILIBILI_ROOM_AREA_ID))
        config.set('bilibili', 'IS_SEND_DAILY_DYNAMIC', str(self.IS_SEND_DAILY_DYNAMIC))
        config.set('bilibili', 'DAILY_DYNAMIC_FORM', str(self.DAILY_DYNAMIC_FORM))
        config.set('bilibili', 'IS_SEND_PRELIVE_DYNAMIC', str(self.IS_SEND_PRELIVE_DYNAMIC))
        config.set('bilibili', 'PRELIVE_DYNAMIC_FORM', str(self.PRELIVE_DYNAMIC_FORM))

        # 直播参数相关设置
        config.set('liveParam', 'LIVE_QUALITY', str(self.LIVE_QUALITY))
        
        config.write(open(self.__CONFIG_PATH, 'w', encoding='utf-8'))