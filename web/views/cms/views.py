import re
import traceback

from flask import render_template, request, url_for, session, redirect, current_app, jsonify

from web.exception import ParameterException, UnknownException, Success
from web.forms import CmsLoginForm, AddUserForm
from web.model.model import User, Category, Articles, Comment
from web.utils.decorators import admin_required
from web.utils import constants
from web import db
from . import cms

from datetime import datetime


@cms.route('/home')
@admin_required
def home():
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return UnknownException()
    data = {
        "user": user
    }
    return render_template('admin/index.html', data=data)


@cms.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = CmsLoginForm().validate_for_api()
        admin = User.verify(form.nick_name.data, form.password.data)
        try:
            admin.last_login = datetime.now()
            db.session.commit()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            db.session.rollback()
            return UnknownException()
        session['user_id'] = admin.id
        return redirect(url_for('cms.home'))
    return render_template('admin/login.html')


@cms.route('/logout')
@admin_required
def logout():
    session['user_id'] = None
    session['username'] = None
    session['user_email'] = None
    return redirect(url_for('cms.login'))


@cms.route('/user_count')
@admin_required
def user_count():
    return render_template('admin/user_count.html')


@cms.route('/user_list')
@admin_required
def user_list():
    page = request.args.get("page", 1)
    key_words = request.args.get("keywords", "")
    try:
        page = int(page)
    except (TypeError, ValueError) as e:
        current_app.logger.error(traceback.format_exc())
        page = 1
    current_page = 1
    total_page = 1
    filters = []
    try:
        if key_words:
            filters.append(User.nick_name.contains(key_words))
        paginate = User.query.filter(*filters).order_by(User.create_time.desc()) \
            .paginate(page=page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT, error_out=False)
        user_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)
        return UnknownException()

    user_dict_list = [user.to_admin_dict() for user in user_list]
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "users": user_dict_list
    }
    return render_template('admin/user_list.html', data=data)


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
@admin_required
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
@admin_required
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
@admin_required
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


@cms.route('/comment/review', methods=['GET', 'POST'])
@admin_required
def comment_review():
    if request.method == 'POST':
        comment_id = request.json.get("comment_id", None)
        status = request.json.get('status', None)
        if not all([comment_id, status]):
            return ParameterException(msg="参与错误")
        comment = Comment.query.get(int(comment_id))
        if not comment:
            return ParameterException(msg="评论不存在")
        comment.status = status
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            db.session.rollback()
            return UnknownException()
        return Success(msg="审核成功")
    page = request.args.get("page", 1)
    key_words = request.args.get("keywords", "")
    try:
        page = int(page)
    except (TypeError, ValueError) as e:
        current_app.logger.error(traceback.format_exc())
        page = 1
    current_page = 1
    total_page = 1
    filters = [Comment.status == 1, Comment.is_delete == 0]
    try:
        if key_words:
            filters.append(Comment.content.contains(key_words))
        paginate = Comment.query.filter(*filters).order_by(Comment.create_time.desc()) \
            .paginate(page=page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT, error_out=False)
        comments = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)
        return UnknownException()
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "comments": comments
    }
    return render_template('admin/comment_review.html', data=data)


@cms.route('/comment/list')
@admin_required
def comment_list():
    page = request.args.get("page", 1)
    key_words = request.args.get("keywords", "")
    try:
        page = int(page)
    except (TypeError, ValueError) as e:
        current_app.logger.error(traceback.format_exc())
        page = 1
    current_page = 1
    total_page = 1
    filters = [Comment.is_delete == 0]
    try:
        if key_words:
            filters.append(Comment.content.contains(key_words))
        paginate = Comment.query.filter(*filters).order_by(Comment.create_time.desc()) \
            .paginate(page=page, per_page=constants.ADMIN_NEWS_PAGE_MAX_COUNT, error_out=False)
        comments = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_page.logger.error(e)
        return UnknownException()
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "comments": comments
    }
    return render_template('admin/comment_list.html', data=data)


@cms.route('/comment/delete', methods=['GET', 'POST'])
@admin_required
def comment_delete():
    comment_id = request.json.get("comment_id")
    if not comment_id:
        return ParameterException("参数为空")
    comment = Comment.query.get(comment_id)
    if not comment:
        return ParameterException("评论不存在")

    comment.is_delete = 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return UnknownException()
    return Success(msg="删除成功")


@cms.route('/user/add', methods=['POST', 'GET'])
@admin_required
def user_add():
    if request.method == 'POST':
        params_dict = request.form
        username = params_dict.get('nick_name', None)
        email_address = params_dict.get('email', None)
        password = params_dict.get('password', None)
        is_admin = params_dict.get('role', None)
        # 参数校验
        if not all([username, email_address, is_admin, password]):
            return ParameterException(msg="=输入参数有空值")
        if not re.match(r'[0-9a-zA-Z]{8,16}', username):
            return ParameterException(msg="用户名格式错误")
        if not re.match(r'^[0-9a-zA-Z)]{0,19}@[0-9]{1,13}\.com', email_address):
            return ParameterException(msg="邮箱格式错误")
            # 新建用户并存储到数据库
        if User.query.filter(User.nick_name == username).first():
            return ParameterException(msg="用户名已存在")
        if User.query.filter(User.email == email_address).first():
            return ParameterException(msg="邮箱已存在")
        user = User()
        user.nick_name = username
        user.email = email_address
        user.password = password
        user.is_admin = int(is_admin)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            db.session.rollback()
            return UnknownException()
        return Success(msg="添加成功")
    info = {
        'roles': [
            {
                'id': 0,
                'name': "普通用户"
            },
            {
                'id': 1,
                'name': '管理员'
            }
        ]
    }
    return render_template('admin/user_add.html', info=info)
