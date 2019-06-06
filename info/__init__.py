from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

db = SQLAlchemy()


def create_app(config_name):
    """
    Create different app based on different environments
    :param config_name: different configuration environments
    :return: app
    """
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
