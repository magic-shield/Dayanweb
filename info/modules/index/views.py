from flask import render_template, current_app, redirect

from info.modules.index import index_blu


@index_blu.route('/')
def index():
    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    return redirect("static/news/favicon.ico")
