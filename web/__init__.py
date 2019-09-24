import json
import logging
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime, date
from flask import Flask, request, g, make_response
from flask_cors import CORS
from flask_mail import Mail
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from redis import StrictRedis
from flask.json import JSONEncoder as _JSONEncoder
from flask_wtf.csrf import generate_csrf
from flask_ckeditor import CKEditor
from werkzeug.exceptions import HTTPException

from web.config.config import config
from web.exception import APIException, UnknownException
from .logger import Log

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
        # model需继承MixinJSONSerializer
        # MixinJSONSerializer里实现了keys 和__getitem__方法,方便将自定义对象转化为字典
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
    from web.views.aux import aux
    app.register_blueprint(user)
    app.register_blueprint(article)
    app.register_blueprint(home)
    app.register_blueprint(cms)
    app.register_blueprint(aux)


def register_template_filter(app):
    from web.utils.common import do_index_class
    app.add_template_filter(do_index_class, "indexClass")


def register_before_request(app):
    @app.before_request
    def request_cost_time():
        g.request_start_time = time.time()
        g.request_time = lambda: "%.5f" % (time.time() - g.request_start_time)


def register_after_request(app):
    @app.after_request
    def log_response(resp):
        message = '[%s] -> [%s] from:%s costs:%.3f ms' % (
            request.method,
            request.path,
            request.remote_addr,
            float(g.request_time()) * 1000
        )
        req_body = '{}'
        try:
            req_body = request.get_json() if request.get_json() else {}
            req_form_data = request.form if request.form else {}
        except:
            pass
        message += " data:{\n\tparam: %s, \n\tbody: %s\n,\n\tform data: %s\n} " % (
            json.dumps(request.args, ensure_ascii=False),
            req_body,
            req_form_data
        )
        # resp = flask.wrappers.Response,as_text=True表示Unicode字符串输出，False表示字节类型输出
        if resp.content_type == "application/json":
            app.logger.info(message + "\n" + "response -> " + resp.get_data(as_text=True))

        # 返回csrf token值
        csrf_token = generate_csrf()
        resp.set_cookie("csrf_token", csrf_token)
        return resp


def create_app(config_name):
    # setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config.from_object("web.config.log")
    db.init_app(app)
    mail.init_app(app)
    global redis_store
    # decode_responses设置为True，自动将字节数据解析
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT, decode_responses=True)
    Log(app)
    Session(app)  # 需要在config文件对session进行配置存储位置等
    Bootstrap(app)
    CORS(app)
    CKEditor(app)
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
            # 在所有视图函数或者model中，除了需要添加或者更新需要手动捕获异常，回滚，其他地方不需要捕获，交给errorhandler处理
            # 如果不是debug模式，就将异常输入到log文件中,并返回UnknownException
            if not app.config['DEBUG']:
                import traceback
                app.logger.error(traceback.format_exc())
                return UnknownException()
            else:
                raise e

    # 注册蓝图
    register_blu(app)
    # 请求生命周期函数
    register_before_request(app)
    register_after_request(app)
    # 注册自定义模板过滤器
    register_template_filter(app)
    return app
