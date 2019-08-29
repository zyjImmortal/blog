from flask import render_template
from . import home


@home.route('/')
def index():
    return render_template('blogs/index.html')