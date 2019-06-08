import logging

from redis import StrictRedis


class Config(object):
    """Integrated configuration Classes"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/dayanweb"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2


class DevelopConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.ERROR


class TestingConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.NOTSET


config = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "testing": TestingConfig
}
