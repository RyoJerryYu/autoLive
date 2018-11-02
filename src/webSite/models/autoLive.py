from src.utitls import loadJson
from src.Configs import CONFIGs
from src.liveScheduler import LiveScheduler
from src.login_bilibili import login_bilibili
from datetime import datetime
from flask import url_for

__default_table_title = ['时间', 'Vtuber', '直播网站', '自定义标题']

def header_menus():
    '''返回layer模板中所用的header_menu
    '''
    header_menus = [
        {
            'name': 'にじさんじ常用网站',
            'Is_dropdown': True,
            'Is_new_tab': True,
            'contains':[
                {
                    'name': 'YouTubeのコメントを見るやつ',
                    'url': r'https://2434.fun/'
                },
                {
                    'name': 'にじさんじwiki',
                    'url': r'https://wikiwiki.jp/nijisanji/'
                },
                {
                    'name': 'SEEDs24H',
                    'url': r'https://2434dola.wixsite.com/seeds24h-official'
                },
                {
                    'name': '今週のかえみと',
                    'url': r'https://mato-liver.com/archives/category/kemt'
                },
            ]
        },
        {
            'name': '时间表',
            'Is_dropdown': False,
            'Is_new_tab': False,
            'url': url_for('autoLive.schedule')
        },
        {
            'name': '设置',
            'Is_dropdown': False,
            'Is_new_tab': False,
            'url': url_for('autoLive.configs')
        }
    ]
    return header_menus

def schedule_sections():
    '''返回schedule页所需的数据
    '''
    # 获得site列表 现在可用的只有YouTube
    sites = ['YouTube']

    # 获得liver列表
    lives_info = loadJson(CONFIGs().LIVE_INFO_PATH)
    livers = []
    for live_info in lives_info:
        livers.append(live_info['liver'])
    
    # 获得查看时间表预定中所需的列表
    lives = LiveScheduler().get_lives()
    rows = []
    # 获取时将时间表按时间排序
    for live_id, live in sorted(lives.items(), key=lambda kv: kv[1].time):
        rows.append(
            {
                'values':[
                    live.time.strftime(r'%m.%d %H:%M'),
                    live.liver,
                    live.site,
                    live.title
                ],
                'id': live_id
            }
        )
    
    # 获得查看运行中项目所需的job列表
    jobs = []
    for live_id, job in LiveScheduler().get_livings().items():
        running_rows=[
            {'title': 'YouTuber', 'value': job['live'].liver},
            {'title': '直播网站', 'value': job['live'].site},
            {'title': '直播间自定义标题', 'value': job['live'].title},
            {'title': '预计开始时间', 'value': job['live'].time},
            {'title': '实际开始时间', 'value': job['startT']},
            {'title': '持续时间', 'value': datetime.now() - job['startT']}
        ]
        jobs.append(
            {
                'title': live_id,
                'rows': running_rows
            }
        )

    # 添加直播项中需要的值
    add_job_value = {
        'title': '添加新项目',
        'descr': '添加时间表项目。\n'\
                 '其中时间一栏填入HHMM格式的四位数字，代表未来24小时内对应日本时区的时间。\n'\
                 '目前只能接受未来24小时内开始的直播。如要立即开播，填入1分钟后的日本时区时间即可。\n'\
                 '自定义标题可不填，不填时默认值为"YouTuber名+转播"。',
        'table_titles': __default_table_title,
        'row': [
            {'input_type': 'text', 'name': 'time'},
            {'input_type': 'select', 'name': 'liver', 'contains': livers},
            {'input_type': 'select', 'name': 'site', 'contains': sites}, 
            {'input_type': 'text', 'name': 'title'}
        ]
    }

    # 查看时间表中需要的值
    schedule_jobs_value = {
        'title': '已注册项目',
        'descr': '时间表中预定要运行的项目。\n'\
                 '时间一栏为日本时区时间。\n'\
                 '每天会在本地时间下午15时在B站发送一次每日时间表动态，内容即为当时此时间表内的内容。\n'\
                 '表内的项目不一定都能转播成功，直播更改日期或是延迟20分钟以上都不能转播成功。',
        'table_titles': __default_table_title,
        'rows': rows
    }

    # 查看运行中项目所需要的值
    running_jobs_value = {
        'title': '运行中的项目',
        'descr': '正在运行中的项目。\n'\
                 '其中的项目不一定都正在转播，有可能是直播开始前正在尝试开始转播，或是直播结束后正在尝试掉线重连。',
        'jobs': jobs
    }

    sections = {
        'add_job': add_job_value,
        'schedule_jobs': schedule_jobs_value,
        'running_jobs': running_jobs_value
    }
    return sections


def configs_sections():
    '''返回设置页面所需数据
    '''
    config = CONFIGs()

    # BILIBILI_ROOM_AREA_ID所需的分区列表
    b = login_bilibili(config.COOKIES_TXT_PATH)
    area_list_data = b.getLiveAreaList()
    area_list = []
    for zone in area_list_data:
        for area in zone['list']:
            if area['lock_status'] == '0':
                area_list.append(
                    {'value': int(area['id']), 'display': area['name']}
                )

    # bilibili
    item_BILIBILI_ROOM_TITLE = {
        'title': '直播间标题格式',
        'input_type': 'text',
        'name': 'BILIBILI_ROOM_TITLE',
        'value': config.BILIBILI_ROOM_TITLE
    }
    item_DEFAULT_TITLE_PARAM = {
        'title': '默认title参数格式',
        'input_type': 'text',
        'name': 'DEFAULT_TITLE_PARAM',
        'value': config.DEFAULT_TITLE_PARAM
    }
    item_BILIBILI_ROOM_AREA_ID = {
        'title': '直播间分区',
        'input_type': 'select',
        'name': 'BILIBILI_ROOM_AREA_ID',
        'value': config.BILIBILI_ROOM_AREA_ID,
        'options': area_list
    }
    item_IS_SEND_DAILY_DYNAMIC = {
        'title': '发送每日转播列表动态',
        'input_type': 'checkbox',
        'name': 'IS_SEND_DAILY_DYNAMIC',
        'value': config.IS_SEND_DAILY_DYNAMIC
    }
    item_DAILY_DYNAMIC_FORM = {
        'title': '每日转播列表动态格式',
        'input_type': 'text',
        'name': 'DAILY_DYNAMIC_FORM',
        'value': config.DAILY_DYNAMIC_FORM
    }
    item_IS_SEND_PRELIVE_DYNAMIC = {
        'title': '转播前发送动态',
        'input_type': 'checkbox',
        'name': 'IS_SEND_PRELIVE_DYNAMIC',
        'value': config.IS_SEND_PRELIVE_DYNAMIC
    }
    item_PRELIVE_DYNAMIC_FORM = {
        'title': '转播前动态格式',
        'input_type': 'text',
        'name': 'PRELIVE_DYNAMIC_FORM',
        'value': config.PRELIVE_DYNAMIC_FORM
    }
    section_bilibili = {
        'title': 'BILIBILI',
        'descr': 'B站直播间与动态相关设置',
        'items': [
            item_BILIBILI_ROOM_TITLE,
            item_DEFAULT_TITLE_PARAM,
            item_BILIBILI_ROOM_AREA_ID,
            item_IS_SEND_DAILY_DYNAMIC,
            item_DAILY_DYNAMIC_FORM,
            item_IS_SEND_PRELIVE_DYNAMIC,
            item_PRELIVE_DYNAMIC_FORM,
        ]
    }

    # liveParam
    item_LIVE_QUALITY = {
        'title': '最高清晰度',
        'input_type': 'select',
        'name': 'LIVE_QUALITY',
        'value': config.LIVE_QUALITY,
        'options': [
            {'value': 0, 'display': 0},
            {'value': 240, 'display': 240},
            {'value': 360, 'display': 360},
            {'value': 480, 'display': 480},
            {'value': 720, 'display': 720},
            {'value': 1080, 'display': 1080},
        ]
    }
    section_liveParam = {
        'title': 'liveParam',
        'descr': '清晰度等直播相关设定',
        'items': [
            item_LIVE_QUALITY,
        ]
    }

    sections = {
        'bilibili': section_bilibili,
        'liveParam': section_liveParam,
    }
    return sections