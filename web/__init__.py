import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, date
from flask import Flask
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis import StrictRedis
from flask.json import JSONEncoder as _JSONEncoder
from werkzeug.exceptions import HTTPException

from config import config
from web.exception import APIException, UnknownException

db = SQLAlchemy()
mail = Mail()
redis_store = None  # type:StrictRedis


def setup_log(config_name):
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        # hasattr判断一个对象是否有name属性或者name方法，hasattr(o,name)
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        return JSONEncoder.default(self, o)


def register_blu(app):
    from web.views.user import user
    from web.views.article import article
    from web.views.home import home
    from web.views.cms import cms
    app.register_blueprint(user)
    app.register_blueprint(article)
    app.register_blueprint(home)
    app.register_blueprint(cms)


def create_app(config_name):
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    mail.init_app(app)
    global redis_store
    # decode_responses设置为True，自动将字节数据解析
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT, decode_responses=True)
    Session(app)  # 需要在config文件对session进行配置存储位置等
    # CORS(app)
    # 自定义json序列化对象
    app.json_encoder = JSONEncoder

    # 注册全局错误处理器
    @app.errorhandler(Exception)
    def handler(e):
        if isinstance(e, APIException):
            return e
        if isinstance(e, HTTPException):
            code = e.code
            msg = e.description
            error_code = 20000
            return APIException(msg, code, error_code)
        else:
            if not app.config['DEBUG']:
                import traceback
                app.logger.error(traceback.format_exc())
                return UnknownException()
            else:
                raise e

    # 注册蓝图
    register_blu()

    return app
