from flask import render_template

from info.modules.index import index_blu


@index_blu.route('/')
def index():
    return render_template("news/index.html")
