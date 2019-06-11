from flask import render_template, g, current_app, abort, jsonify

from info import constants
from info.models import News
from info.modules.news import news_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@news_blu.route("/<int:news_id>")
@user_login
def detail(news_id):
    """
    详情页面渲染
    :param news_id:
    :return:
    """
    user = g.user

    # --显示点击排行新闻--
    clicks_news = list()
    try:
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    clicks_news_li = [news.to_dict() for news in clicks_news]

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li
    }
    return render_template("news/detail.html", data=data)
