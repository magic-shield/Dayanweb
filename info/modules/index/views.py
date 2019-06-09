from flask import render_template, current_app, session

from info import constants
from info.models import User, News
from info.modules.index import index_blu


@index_blu.route('/')
def index():
    user_id = session.get("user_id")

    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger(e)

    # 显示新闻点击排行
    clicks_news = list()
    try:
        # 以点击量降序取出新闻, 结果是对象列表
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    # 转化为字典列表
    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
