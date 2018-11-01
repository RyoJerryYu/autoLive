from flask import Blueprint
from flask import render_template, redirect, url_for, abort
from flask import request as flRequest

from src.webSite.models.autoLive import header_menus, schedule_sections, configs_sections
from src.liveScheduler import LiveScheduler, Live
from src.rebroadcast import rebroadcast
from src.Configs import CONFIGs

mod = Blueprint('autoLive', __name__, url_prefix='/autoLive')


@mod.route('/')
def autoLive_root():
    if len(flRequest.args) != 0:
        abort(401)
    return redirect(url_for('autoLive.schedule'))

@mod.route('/schedule', methods=['GET', 'POST'])
def schedule():
    '''处理时间表增删查的网页

    增加项目时POST存在参数Add
    删除项目时POST存在参数Delete
    Delete的值为删除项的live_id
    '''
    if flRequest.method == 'POST':
        if flRequest.form.get('Add', None):
            try:
                live = Live(
                    time=flRequest.form['time'],
                    liver=flRequest.form['liver'],
                    site=flRequest.form['site'],
                    title=flRequest.form['title']
                )
                LiveScheduler().add_live(rebroadcast, live)
            except Exception:
                pass
        elif flRequest.form.get('Delete', None):
            LiveScheduler().pop_live(flRequest.form['Delete'])
        else:
            abort(401)
    return render_template(
        'scheduler.html', 
        header_menus=header_menus(), 
        form_action=url_for('autoLive.schedule'), 
        sections=schedule_sections()
    )

@mod.route('/configs', methods=['GET', 'POST'])
def configs():
    '''设置页面

    POST访问时动作由参数Action值决定
    为Apply时应用form中设置
    为Reset时丢弃form中设置
    '''
    if flRequest.method == 'POST' and flRequest.form['Action'] == 'Apply':
        config = CONFIGs()

        config.BILIBILI_ROOM_TITLE = flRequest.form['BILIBILI_ROOM_TITLE']
        config.DEFAULT_TITLE_PARAM = flRequest.form['DEFAULT_TITLE_PARAM']
        config.BILIBILI_ROOM_AREA_ID = int(flRequest.form['BILIBILI_ROOM_AREA_ID'])
        config.IS_SEND_DAILY_DYNAMIC = True if flRequest.form.get('IS_SEND_DAILY_DYNAMIC') else False
        config.DAILY_DYNAMIC_FORM = flRequest.form['DAILY_DYNAMIC_FORM']
        config.IS_SEND_PRELIVE_DYNAMIC = True if flRequest.form.get('IS_SEND_PRELIVE_DYNAMIC') else False
        config.PRELIVE_DYNAMIC_FORM = flRequest.form['PRELIVE_DYNAMIC_FORM']

        config.LIVE_QUALITY = int(flRequest.form['LIVE_QUALITY'])
        config.save_configs()
    return render_template(
        'configs.html',
        header_menus=header_menus(),
        form_action=url_for('autoLive.configs'),
        sections=configs_sections()
    )