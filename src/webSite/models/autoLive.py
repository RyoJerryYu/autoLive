from src.utitls import loadJson
from src.Configs import CONFIGs
from src.liveScheduler import LiveScheduler
from datetime import datetime

__default_table_title = ['时间', 'Vtuber', '直播网站', '自定义标题']

def header_menus():
    '''返回layer模板中所用的header_menu
    '''
    header_menus = [
        {
            'name': 'にじさんじ常用网站',
            'Is_dropdown': True,
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
        'title': '添加',
        'descr': '添加时间表项目',
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
        'descr': '时间表中将要运行的项目',
        'table_titles': __default_table_title,
        'rows': rows
    }

    # 查看运行中项目所需要的值
    running_jobs_value = {
        'title': '运行中的项目',
        'descr': '正在运行中的项目，可能会出现偏差',
        'jobs': jobs
    }

    sections = {
        'add_job': add_job_value,
        'schedule_jobs': schedule_jobs_value,
        'running_jobs': running_jobs_value
    }
    return sections