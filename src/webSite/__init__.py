from flask import Flask

web = Flask(__name__)

from src.webSite.views import autoLive
web.register_blueprint(autoLive.mod)
