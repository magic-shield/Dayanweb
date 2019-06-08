from flask import abort, current_app, make_response, request

from info import redis_store, constants
from info.modules.passport import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route("/image_code")
def get_image_code():
    # Get parameters
    image_code_id = request.args.get("imageCodeId")

    # Check if the parameter exists
    if not image_code_id:
        abort(404)

    # Generate captcha
    _, text, image = captcha.generate_captcha()

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
    # get param: mobile, image_code, image_code_id
    # global check
    # Verify mobile
    # Verify if the picture captcha expires
    # Verify that the verification code entered by the user is the same as the verification code queried through the image_code_id

    pass