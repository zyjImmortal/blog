from functools import wraps
from flask import redirect, url_for, flash
from web.exception import AuthFailed
from web.utils.common import get_current_user


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_admin:
            return AuthFailed(msg="只有管理员可以操作")
        return fn(*args, **kwargs)

    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("请先登录后，方可操作", 'warning')
            return redirect(url_for('cms.login'))
        return fn(*args, **kwargs)

    return wrapper
