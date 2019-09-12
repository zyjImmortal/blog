from flask import render_template, current_app, request

from web.model.model import Category
from web.utils.decorators import admin_required
from web.exception import UnknownException
from . import article


@article.route('/list')
def articles():
    pass


@article.route('/add', methods=['POST', 'GET'])
@admin_required
def add_article():
    if request.method == "POST":
        pass
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    info = {
        'categories': categories
    }
    return render_template('admin/article_add.html', info=info)
