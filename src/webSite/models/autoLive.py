from src.utitls import loadJson
from src.Configs import CONFIGs
from src.liveScheduler import LiveScheduler
from datetime import datetime

__default_table_title = ['时间', 'Vtuber', '直播网站', '自定义标题']

def header_menus():
    return []

def schedule_sections():
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
    for live_id, live in lives.items():
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

    sections = {
        'add_job': add_job_value,
        'schedule_jobs': schedule_jobs_value
    }
    return sections