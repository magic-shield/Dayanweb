from flask import g, redirect, render_template

from info.utils.common import user_login
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


@profile_blu.route("/user_base_info")
@user_login
def user_base_info():
    """
    个人中心基本资料
    :return:
    """
    user = g.user

    data = {
        "user_info": user.to_dict()
    }

    return render_template("news/user_base_info.html", data=data)
