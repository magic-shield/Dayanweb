import datetime

from flask import render_template, request, current_app, session, g, redirect, url_for

from info import user_login
from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    """
    渲染后台登录界面
    :return:
    """

    if request.method == "GET":
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))

        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数错误")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == 1).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="用户信息查询失败")

    if not user:
        return render_template('admin/login.html', errmsg="未查询到用户信息")

    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="用户名或者密码错误")

    session["user_id"] = user.id
    session["is_admin"] = user.is_admin

    return redirect(url_for("admin.index"))


@admin_blu.route("/index")
@user_login
def index():
    """
    后台管理首页
    :return:
    """
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("admin/index.html", data=data)


@admin_blu.route("/user_count")
def user_count():
    """
    用户统计
    :return:
    """
    # 总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == 0).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数, 先获取今天的时间对象, 制造时间字符串类似"2019-03-01"
    month_count = 0
    t = datetime.datetime.now()
    month_date_str = "%d-%02d-01" % (t.year, t.month)
    # 将字符串转成datetime对象
    month_date = datetime.datetime.strptime(month_date_str, "%Y-%m-%d")
    try:
        month_count = User.query.filter(User.is_admin == 0, User.create_time > month_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    day_date_str = "%d-%02d-%02d" % (t.year, t.month, t.day)
    day_date = datetime.datetime.strptime(day_date_str, "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_date).count()
    except Exception as e:
        current_app.logger.error(e)

    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
    }

    return render_template("admin/user_count.html", data=data)
