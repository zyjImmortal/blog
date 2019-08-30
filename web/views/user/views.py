from flask import request, current_app
import re
from web.exception import ParameterException, UnknownException, Success
from web.model.model import User
from . import user
from web.utils.common import random_email_code, send_register_mail_code
from web.utils.redis_util import RedisUtil
from web.utils import constants
from web import mail, db


@user.route('/register', methods=['POST'])
def register():
    params_dict = request.json
    username = params_dict.get('username', None)
    email_address = params_dict.get('email_address', None)
    email_code = params_dict.get('email_code', None)
    password = params_dict.get('password', None)
    # 参数校验
    if not all([username, email_address, email_code, password]):
        return ParameterException(msg="=输入参数有空值")
    if not re.match(r'[0-9a-zA-Z]{8,16}', username):
        return ParameterException(msg="用户名格式错误")
    if not re.match(r'^[0-9a-zA-Z)]{0,19}@[0-9]{1,13}\.com', email_address):
        return ParameterException(msg="邮箱格式错误")
    try:
        real_email_code = RedisUtil.get(constants.EMAIL_CODE_KEY + email_address)
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    if real_email_code != email_code:
        return ParameterException(msg="验证码错误")
    # 新建用户并存储到数据库
    user = User()
    user.nick_name = username
    user.email = email_address
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return UnknownException()
    return Success(msg="注册成功")


@user.route('/email_code', methods=['POST'])
def get_email_code():
    params_dict = request.json
    username = params_dict.get('username', None)
    email_address = params_dict.get('email_address', None)
    if not all([username, email_address]):
        return ParameterException(msg="用户名或邮箱为空")
    if not re.match(r'[0-9a-zA-Z]{8,16}', username):
        return ParameterException(msg="用户名格式错误")
    if not re.match(r'^[0-9a-zA-Z)]{0,19}@[0-9]{1,13}\.com', email_address):
        return ParameterException(msg="邮箱格式错误")
    email_code = random_email_code()
    try:
        RedisUtil.set(constants.EMAIL_CODE_KEY + email_address, email_code)
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    send_register_mail_code(mail, email_address, username, email_code)
    return Success(msg="验证码发送成功")


@user.route('/login', methods=['POST'])
def login():
    pass
