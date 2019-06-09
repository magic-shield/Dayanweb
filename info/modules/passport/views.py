import random
import re
from datetime import datetime

from flask import abort, current_app, make_response, request, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/image_code")
def get_image_code():
    image_code_id = request.args.get("imageCodeId")

    if not image_code_id:
        abort(404)

    _, text, image = captcha.generate_captcha()

    current_app.logger.info("图片验证码为" + text)  # TEST

    try:
        redis_store.setex("ImageCodeID_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        real_image_code = redis_store.get("ImageCodeID_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    sms_code_str = "%06d" % random.randint(0, 999999)

    current_app.logger.info("短信验证码为" + sms_code_str)  # TEST

    # Call yuntongxun to send sms verification code
    # result = CCP().send_template_sms('mobile', [sms_code_str, 5], 1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")


    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码保存失败")

    return jsonify(errno=RET.OK, errmsg="成功发送短信验证码")


@passport_blu.route("/register", methods=["POST"])
def register():
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码已经过期")

    if smscode != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    user = User()
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")



@passport_blu.route("/login", methods=["POST"])
def login():
    """
    1.接收参数
    2.校验参数 手机号格式, 密码是否正确
    3.保持用户登录状态
    4.返回响应
    5.设置用户登录时间
    :return:
    """

    dict_data = request.json
    mobile = dict_data.get("mobile")
    passport = dict_data.get("passport")

    if not all([mobile, passport]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户没有注册")

    if not user.check_passowrd(passport):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg="登陆成功")



@passport_blu.route("/logout")
def logout():
    """退出功能:直接删除session"""
    session.pop("user_id", None)
    return jsonify(errno=RET.OK, errmsg="退出成功")

