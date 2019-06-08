from flask import abort, current_app, make_response, request

from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route("/image_code")
def get_image_code():
    """
    获取参数(随机的字符串)
    校验参数是否存在
    生成验证码 captcha
    随机字符串和生成的文本验证码以k,v的形式保存到redis中
    把图片验证码返回给浏览器
    :return:
    """

    image_code_id = request.args.get("imageCodeId")

    if not image_code_id:
        abort(404)

    _, text, image = captcha.generate_captcha()

    try:
        redis_store.setex("ImageCodeID_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"
    return response
