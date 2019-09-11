from flask import render_template, request, url_for, session, redirect, current_app, jsonify

from web.exception import ParameterException, UnknownException, Success
from web.forms import CmsLoginForm
from web.model.model import User, Category
from web.utils.decorators import admin_required
from web import db
from . import cms


@cms.route('/home')
@admin_required
def home():
    return render_template('admin/index.html')


@cms.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = CmsLoginForm().validate_for_api()
        admin = User.verify(form.nick_name.data, form.password.data)
        session['nick_name'] = admin.nick_name
        session['password'] = admin.password
        return redirect(url_for('cms.home'))
    return render_template('admin/login.html')


@cms.route('/user_count.html')
@admin_required
def user_count():
    return render_template('admin/user_count.html')


@cms.route('/user_list.html')
@admin_required
def user_list():
    return render_template('admin/user_list.html')


@cms.route('/news_review.html')
@admin_required
def news_review():
    return render_template('admin/news_review.html')


@cms.route('/article/review', methods=["POST"])
@admin_required
def article_review():
    pass


@cms.route('/news_type.html')
@admin_required
def news_type():
    page = request.args.get('page', 1, type=int)
    paginate_categories = Category.query.paginate(page, per_page=10, error_out=False)
    category_info = {
        "count": paginate_categories.count,
        "data": paginate_categories.items
    }
    return render_template('admin/news_type.html')


@cms.route('/categories')
def categories():
    page = request.args.get('page', 1, type=int)
    paginate_categories = Category.query.paginate(page, per_page=10, error_out=False)
    category_info = {
        "total": paginate_categories.total,
        "list": paginate_categories.items
    }
    return Success(msg="请求成功", data=category_info)


@cms.route('/news_edit.html')
@admin_required
def news_edit():
    return render_template('admin/news_edit.html')


@cms.route('/news_edit_detail.html')
@admin_required
def news_edit_detail():
    return render_template('admin/news_edit_detail.html')


@cms.route('/news_review_detail.html')
@admin_required
def news_review_detail():
    return render_template('admin/news_review_detail.html')


@cms.route('/category/add', methods=["POST"])
def add_category():
    category_name = request.json.get("name", None)
    if not category_name:
        return ParameterException(msg="分类名称不能为空")
    try:
        category = Category.query.filter_by(name=category_name).first()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    if category:
        return ParameterException(msg="分类名称已存在")
    new_category = Category()
    new_category.name = category_name

    try:
        db.session.add(new_category)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    return Success(msg="添加成功")


@cms.route('/category/edit', methods=["POST"])
def edit_category():
    category_id = request.json.get("id", None)
    category_name = request.json.get("name", None)
    if not category_name:
        return ParameterException(msg="分类名称不能为空")
    try:
        category = Category.query.filter_by(id=category_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    if not category:
        return ParameterException(msg="该分类不存在")
    if category_name == category.name:
        return ParameterException(msg="分类名称与旧名称相同")
    category.name = category_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    return Success(msg="修改成功")
