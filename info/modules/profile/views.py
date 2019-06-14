from flask import g, redirect, render_template, request, jsonify, current_app

from info import db
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
