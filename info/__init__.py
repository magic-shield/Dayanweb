import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

db = SQLAlchemy()


def set_log(config_name):
    """Create different logs based on different environments"""
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = RotatingFileHandler("/home/python/Desktop/Dayanweb/logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


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

    # Integrated redis
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)

    # Integrated CSRFProtect
    CSRFProtect(app)

    # Integrated flask-session
    Session(app)

    return app
