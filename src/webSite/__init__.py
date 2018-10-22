from flask import Flask
from flask import render_template, redirect, url_for
from flask import request as flRequest

web = Flask(__name__)

from src.webSite.views import autoLive
web.register_blueprint(autoLive.mod)
