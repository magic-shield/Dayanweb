from flask import Blueprint

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")

from .views import *


@admin_blu.before_request
def admin_identification():
    is_login = request.url.endswith("/admin/login")
    is_admin = session.get("is_admin")
    if not is_admin and not is_login:
        return redirect("/")
