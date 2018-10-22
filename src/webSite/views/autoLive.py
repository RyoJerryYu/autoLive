from flask import Blueprint
from flask import render_template, redirect, url_for, abort
from flask import request as flRequest

from src.webSite.models.autoLive import header_menus, schedule_sections
from src.liveScheduler import LiveScheduler, Live
from src.rebroadcast import rebroadcast

mod = Blueprint('autoLive', __name__, url_prefix='/autoLive')


@mod.route('/')
def autoLive_root():
    return redirect(url_for('autoLive.schedule'))

@mod.route('/schedule', methods=['GET', 'POST'])
def schedule():
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