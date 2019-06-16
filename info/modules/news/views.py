from flask import render_template, g, current_app, abort, jsonify, request

from info import constants, db
from info.models import News, Comment, CommentLike
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

    # --显示具体的新闻内容--
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        abort(404)

    # --点击量设置--
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库存储失败")

    # --收藏和取消收藏标签显示--
    is_collected = False
    if user and (news in user.collection_news):
        is_collected = True

    # --关注按钮显示--
    is_followed = False
    author = news.user
    if user and author:
        # 如果用户在作者的粉丝列表中
        if user in author.followers:
            is_followed = True

    # --显示新闻评论--
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # comments_dict_li = [comment.to_dict() for comment in comments]

    # --显示点赞--
    comment_likes_ids = list()
    if user:
        # 取出当前新闻下的所有的评论id列表
        comment_ids = [comment.id for comment in comments]
        # 查询出当前用户点过赞的评论对象
        comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id, CommentLike.comment_id.in_(comment_ids)).all()
        # 遍历出当前用户点过赞的评论对象的id列表
        comment_likes_ids = [comment_like.comment_id for comment_like in comment_likes]

    comments_dict_li = list()
    for comment in comments:
        comment_dict = comment.to_dict()
        # 给每一条评论都添加一个字段is_like,并默认为False
        comment_dict["is_like"] = False
        # 如果该条评论在点过赞的评论id列表中, 将is_like改为True
        if comment.id in comment_likes_ids:
            comment_dict["is_like"] = True
        comments_dict_li.append(comment_dict)

    data = {
        "user_info": user.to_dict() if user else None,
        "clicks_news_li": clicks_news_li,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments_dict_li": comments_dict_li,
        "is_followed": is_followed
    }
    return render_template("news/detail.html", data=data)


@news_blu.route("/news_collect", methods=["POST"])
@user_login
def news_collect():
    """
    新闻收藏和取消收藏功能
    :return:
    """
    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    news_id = request.json.get("news_id")
    action = request.json.get("action")

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="没有这条新闻")

    if action == "collect":
        if news not in user.collection_news:
            user.collection_news.append(news)
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="数据库保存错误")
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.DBERR, errmsg="数据库保存错误")

    return jsonify(errno=RET.OK, errmsg="OK")


@news_blu.route("/news_comment", methods=["POST"])
@user_login
def news_comment():
    """
    新闻评论功能
    :return:
    """

    user = g.user

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all([news_id, comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="没有这条新闻")

    # 初始化模型对象, 并往数据库添加一条评论
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@news_blu.route("/comment_like", methods=["POST"])
@user_login
def get_comment_like():
    """
    评论点赞功能
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    try:
        comment_obj = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not comment_obj:
        return jsonify(errno=RET.NODATA, errmsg="没有这条评论")

    try:
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                CommentLike.user_id == user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if action == "add":
        if not comment_like:
            comment_like_obj = CommentLike()
            comment_like_obj.comment_id = comment_id
            comment_like_obj.user_id = user.id
            db.session.add(comment_like_obj)
            comment_obj.like_count += 1
    else:
        if comment_like:
            db.session.delete(comment_like)
            comment_obj.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")
