from flask import render_template, g

from info.modules.news import news_blu
from info.utils.common import user_login


@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    user = g.user

    data = {
        "user_info": user.to_dict() if user else None
    }
    return render_template("news/detail.html", data=data)
