from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)


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
    PERMANENT_SESSION_LIFETIME = 5


app.config.from_object(Config)

# Integrated SQLAlchemy to Flask
db = SQLAlchemy(app)

# Integrated redis
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# Integrated CSRFProtect
CSRFProtect(app)

# Integrated flask-session
Session(app)

# Integrated flask-script
manager = Manager(app)

# Integrated flask-migrate
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    return "hello"


if __name__ == '__main__':
    app.run()
