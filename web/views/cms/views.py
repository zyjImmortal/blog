from flask import render_template, request, url_for, session, redirect

from web.forms import CmsLoginForm
from web.model.model import User
from web.utils.decorators import admin_required
from . import cms


@cms.route('/home')
@admin_required
def home():
    return render_template('admin/index.html')


@cms.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = CmsLoginForm().validate_for_api()
        admin = User.verify(form.nick_name, form.password)
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


@cms.route('/news_type.html')
@admin_required
def news_type():
    return render_template('admin/news_type.html')


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
