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
        self.COOKIES_TXT_PATH = config.get('basic', 'COOKIES_TXT_PATH')
        self.LIVE_INFO_PATH = config.get('basic', 'LIVE_INFO_PATH')
        self.SCHEDULE_TXT_PATH = config.get('basic', 'SCHEDULE_TXT_PATH')

        self.BILIBILI_ROOM_TITLE = config.get('live', 'BILIBILI_ROOM_TITLE')
        self.FFMPEG_COMMAND = config.get('live', 'FFMPEG_COMMAND')
        self.BILIBILI_ROOM_AREA_ID = config.getint('live', 'BILIBILI_ROOM_AREA_ID')
        
        self.LIVE_QUALITY = config.getint('youtube-dl', 'LIVE_QUALITY')