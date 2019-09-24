import traceback

from flask import render_template, request, url_for, session, redirect, current_app, jsonify

from web.exception import ParameterException, UnknownException, Success
from web.forms import CmsLoginForm
from web.model.model import User, Category, Articles
from web.utils.decorators import admin_required
from web.utils import constants
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
        session['user_id'] = admin.id
        return redirect(url_for('cms.home'))
    return render_template('admin/login.html')


@cms.route('/user_count')
@admin_required
def user_count():
    return render_template('admin/user_count.html')


@cms.route('/user_list')
@admin_required
def user_list():
    return render_template('admin/user_list.html')


@cms.route('/news_review')
@admin_required
def news_review():
    return render_template('admin/news_review.html')


@cms.route('/article/review', methods=["POST"])
@admin_required
def article_review():
    pass


@cms.route('/news_type')
@admin_required
def news_type():
    categories = Category.query.all()
    return render_template('admin/news_type.html', categories=[category.to_dict() for category in categories])


@cms.route('/categories')
def categories():
    page = request.args.get('page', 1, type=int)
    paginate_categories = Category.query.paginate(page, per_page=10, error_out=False)
    category_info = {
        "total": paginate_categories.total,
        "list": paginate_categories.items
    }
    return Success(msg="请求成功", data=category_info)


@cms.route('/news_edit')
@admin_required
def news_edit():
    page = request.args.get("page", 1)
    key_words = request.args.get("keywords", "")
    try:
        page = int(page)
    except (TypeError, ValueError) as e:
        current_app.logger.error(traceback.format_exc())
        page = 1
    current_page = 1
    total_page = 1

    try:
        filters = [Articles.status == 0]
        if key_words:
            filters.append(Articles.title.contains(key_words))
        paginate = Articles.query.filter(*filters).order_by(Articles.create_time.desc()) \
            .paginate(page=page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT, error_out=False)
        article_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)
        return UnknownException()

    article_dict_list = [article.to_basic_dict() for article in article_list]
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "articles": article_dict_list
    }

    return render_template('admin/news_edit.html', data=data)


@cms.route('/news_edit_detail')
@admin_required
def news_edit_detail():
    return render_template('admin/news_edit_detail.html')


@cms.route('/news_review_detail')
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
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    if category:
        return ParameterException(msg="分类名称已存在")
    new_category = Category()
    new_category.name = category_name

    try:
        db.session.add(new_category)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
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
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    if not category:
        return ParameterException(msg="该分类不存在")
    if category_name == category.name:
        return ParameterException(msg="分类名称与旧名称相同")
    category.name = category_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    return Success(msg="修改成功")
