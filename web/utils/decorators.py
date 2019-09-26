from functools import wraps
from flask import redirect, url_for, flash, g, session
from web.exception import AuthFailed
from web.utils.common import get_current_user


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        g.user = user
        if not user:
            flash("用户不存在")
            return redirect(url_for('cms.login'))
        if not user.is_admin:
            flash("只有管理员可以操作")
            return redirect(url_for('cms.login'))
        return fn(*args, **kwargs)

    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        g.user = user
        if not user:
            flash("请先登录后，方可操作", 'warning')
            return redirect(url_for('cms.login'))
        return fn(*args, **kwargs)

    return wrapper


def user_login_data(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            from web.model.model import User
            user = User.query.get(user_id)
        g.user = user
        return fn(*args, **kwargs)

    return wrapper
