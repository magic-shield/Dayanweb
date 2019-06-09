import random
import re

from flask import abort, current_app, make_response, request, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


@passport_blu.route("/image_code")
def get_image_code():
    # Get parameters
    image_code_id = request.args.get("imageCodeId")

    # Check if the parameter exists
    if not image_code_id:
        abort(404)

    # Generate captcha
    _, text, image = captcha.generate_captcha()

    current_app.logger.info("图片验证码为" + text)  # TEST

    # Save to redis
    try:
        redis_store.setex("ImageCodeID_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # Return image and change the response header
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response


@passport_blu.route("/sms_code", methods=["POST"])
def get_sms_code():
    """
    get param: mobile, image_code, image_code_id
    global check
    Verify mobile
    Verify if the image captcha expires
    Verify that the image captcha entered by the user is the same as the image captcha queried through the image_code_id
    Define a random six-bit sms verification code
    Call yuntongxun to send sms verification code
    Save sms verification code to Redis
    Return response
    """

    # get param: mobile, image_code, image_code_id
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # global check
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # Verify mobile
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # Verify if the image captcha expires
    try:
        real_image_code = redis_store.get("ImageCodeID_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")

    # Verify that the image captcha entered by the user is the same as the image captcha queried through the image_code_id
    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码输入错误")

    # Define a random six-bit sms verification code

    sms_code_str = "%06d" % random.randint(0, 999999)

    current_app.logger.info("短信验证码为" + sms_code_str)  # TEST

    # Call yuntongxun to send sms verification code
    # result = CCP().send_template_sms('mobile', [sms_code_str, 5], 1)
    # if result != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="短信验证码发送失败")


    # Save sms verification code to Redis
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码保存失败")

    # Return response
    return jsonify(errno=RET.OK, errmsg="成功发送短信验证码")


@passport_blu.route("/register", methods=["POST"])
def register():
    """
    1.接收参数 mobile smscode password
    2.整体校验参数
    3.手机号格式是否正确
    4.从redis中通过手机号取出真实的短信验证码
    5.和用户输入的验证码进行校验
    6.初始化user对象,添加数据
    7.session保持用户登录状态
    8.返回响应
    :return:
    """

    # 1.接收参数 mobile smscode password
    dict_data = request.json
    mobile = dict_data.get("mobile")
    smscode = dict_data.get("smscode")
    password = dict_data.get("password")

    # 2.整体校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 3.手机号格式是否正确
    if not re.match(r"1[35678]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 4.从redis中通过手机号取出真实的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码已经过期")

    # 5.和用户输入的验证码进行校验
    if smscode != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 6.初始化user对象,添加数据
    user = User()
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")

    # 7.session保持用户登录状态
    session["user_id"] = user.id

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")






