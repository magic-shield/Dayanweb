from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session

app = Flask(__name__)

app.config.from_object(config["develop"])

# Integrated SQLAlchemy to Flask
db = SQLAlchemy(app)

# Integrated redis
redis_store = StrictRedis(host=config["develop"].REDIS_HOST, port=config["develop"].REDIS_PORT)

# Integrated CSRFProtect
CSRFProtect(app)

# Integrated flask-session
Session(app)
