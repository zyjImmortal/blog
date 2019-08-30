from flask import render_template

from web.exception import Success
from . import home


@home.route('/')
def index():
    return render_template('blogs/index.html')


@home.route('/error')
def error():
    return Success(msg="访问成功")
