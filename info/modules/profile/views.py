from flask import g, redirect, render_template, request, jsonify, current_app

from info import db, constants
from info.libs.image_storage import storage
from info.models import Category, News
from info.utils.common import user_login
from info.utils.response_code import RET
from . import profile_blu


@profile_blu.route("/info")
@user_login
def user_info():
    """
    个人中心界面
    :return:
    """
    user = g.user

    if not user:
        return redirect("/")

    data = {
        "user_info": user.to_dict()
    }

    return render_template("news/user.html", data=data)


@profile_blu.route("/user_base_info", methods=["POST", "GET"])
@user_login
def user_base_info():
    """
    个人中心基本资料
    :return:
    """
    user = g.user

    if request.method == "GET":
        data = {
            "user_info": user.to_dict()
        }

        return render_template("news/user_base_info.html", data=data)

    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="修改成功")


@profile_blu.route("/user_pic_info", methods=["GET", "POST"])
@user_login
def user_pic_info():
    """
    用户头像设置
    :return:
    """
    user = g.user

    if request.method == "GET":
        data = {
            "user_info": user.to_dict()
        }

        return render_template("news/user_pic_info.html", data=data)

    try:
        image_data = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 保存到七牛云
    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="上传头像成功", data=constants.QINIU_DOMIN_PREFIX + key)


@profile_blu.route("/user_pass_info", methods=["GET", "POST"])
@user_login
def user_pass_info():
    """
    用户密码修改
    :return:
    """
    user = g.user

    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码输入错误")

    try:
        user.password = new_password
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_blu.route("/user_collection")
@user_login
def user_collection():
    """
    我的收藏
    :return:
    """
    user = g.user
    page = request.args.get("page", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_dict_li
    }

    return render_template('news/user_collection.html', data=data)


@profile_blu.route("/user_news_release", methods=["POST", "GET"])
@user_login
def user_news_release():
    """
    发布新闻
    :return:
    """
    user = g.user
    if request.method == "GET":
        categorys = Category.query.all()

        categorys_dict_li = [category.to_dict() for category in categorys]

        categorys_dict_li.pop(0)

        data = {
            "categorys_dict_li": categorys_dict_li
        }
        return render_template("news/user_news_release.html", data=data)

    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        category_id = int(category_id)
        image_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数格式不正确")

    try:
        key = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="第三方上传失败")

    news = News()
    news.title = title
    news.source = "个人发布"
    news.digest = digest
    news.content = content
    news.category_id = category_id
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.user_id = user.id
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="OK")
