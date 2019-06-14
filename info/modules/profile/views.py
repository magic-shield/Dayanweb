from flask import g, redirect, render_template, request, jsonify, current_app

from info import db, constants
from info.libs.image_storage import storage
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
