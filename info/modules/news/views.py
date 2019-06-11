from flask import render_template

from info.modules.news import news_blu


@news_blu.route("/<int:news_id>")
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    data = {

    }
    return render_template("news/detail.html", data=data)
