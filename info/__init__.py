import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session

from info.utils.common import do_index_class

db = SQLAlchemy()


def set_log(config_name):
    """Create different logs based on different environments"""
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = RotatingFileHandler("/home/python/Desktop/Dayanweb/logs/log", maxBytes=1024 * 1024 * 100,
                                           backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


redis_store = None  # type: StrictRedis
def create_app(config_name):
    """
    Create different app based on different environments
    :param config_name: different configuration environments
    :return: app
    """

    set_log(config_name)

    app = Flask(__name__)

    app.config.from_object(config[config_name])

    # Integrated SQLAlchemy to Flask
    db.init_app(app)

    global redis_store
    # Integrated redis
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT,
                              decode_responses=True)

    # Integrated CSRFProtect
    # 1.add csrf_token to Cookie
    # 2.add csrf token to Ajax
    @app.after_request
    def after_request(response):
        # Generate token values with WTF extensions
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    CSRFProtect(app)

    # Integrated flask-session
    Session(app)

    # add filter
    app.add_template_filter(do_index_class, "index_class")

    # Register blueprint
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)
    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)

    return app
