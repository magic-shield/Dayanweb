from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


class Config(object):
    """Integrated configuration Classes"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/dayanweb"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


app.config.from_object(Config)

# Integrated SQLAlchemy to Flask
db = SQLAlchemy(app)


@app.route('/')
def index():
    return "hello"


if __name__ == '__main__':
    app.run()
