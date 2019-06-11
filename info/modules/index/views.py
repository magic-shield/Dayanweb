from flask import render_template, current_app, session, request, jsonify, g

from info import constants
from info.models import User, News, Category
from info.modules.index import index_blu
from info.utils.common import user_login
from info.utils.response_code import RET


@index_blu.route('/')
@user_login
def index():
    user = g.user

    # --显示新闻点击排行--
    clicks_news = list()
    try:
        # 以点击量降序取出新闻, 结果是对象列表
        clicks_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    # 转化为字典列表
    clicks_news_li = [news.to_basic_dict() for news in clicks_news]

    # --显示新闻分类--
    categorys = list()
    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    categorys_li = [category.to_dict() for category in categorys]

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "categorys": categorys_li
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")


@index_blu.route("/news_list")
def get_news_list():
    """
    获取新闻列表

    1. GET请求　接收参数 cid	page  per_page
    2. 校验参数合法性
    3. 查询出对应分类下的新闻数据　按照创建时间排序
    4. 返回响应　新闻数据
    :return:
    """
    cid = request.args.get("cid")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    filters = list()
    if cid != 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).\
            order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    news_list = paginate.items
    current_page = paginate.page
    total_page = paginate.pages

    news_dict_li = [news.to_dict() for news in news_list]

    data = {
        "news_dict_li": news_dict_li,
        "current_page": current_page,
        "total_page": total_page
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data)
