from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

app = Flask(__name__)

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
