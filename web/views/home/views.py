import traceback
import json
from flask import render_template, session, current_app, abort, request, g, jsonify

from web import db
from web.exception import Success, UnknownException, ParameterException
from web.model.model import User, Articles, Category, Comment
from web.utils import constants
from web.utils.decorators import user_login_data
from . import home


@home.route('/')
def index():
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return UnknownException()
    articles = []
    try:
        articles = Articles.query.order_by(Articles.clicks.desc()).limit(current_app.config['TOP_CLICK_COUNTS'])
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    articles_info = [article.to_dict() for article in articles]

    # 分类信息
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    try:
        article_list = Articles.query.filter_by(status=0).order_by(Articles.clicks.desc()).limit(
            constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    click_articles_list = []
    for article_click in article_list if article_list else []:
        click_articles_list.append(article_click.to_basic_dict())

    info = {
        'user_info': user.to_dict() if user else None,
        'articles_info': articles_info,
        'categories': categories,
        "click_articles_list": click_articles_list
    }
    return render_template('blogs/index.html', data=info)


@home.route("/article/<int:article_id>")
def article_detail(article_id):
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return UnknownException()
    try:
        article = Articles.query.get(article_id)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        abort(404)
        # 分类信息
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    if not article:
        # 返回数据未找到的页面
        abort(404)

    try:
        article_click_list = Articles.query.filter_by(status=0).order_by(Articles.clicks.desc()).limit(
            constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    try:
        article_list = Articles.query.filter_by(status=0,).limit(
            constants.OTHER_NEWS_PAGE_MAX_COUNT)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    click_articles_list = []
    for article_click in article_click_list if article_click_list else []:
        click_articles_list.append(article_click.to_basic_dict())

    article.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return UnknownException()

    comments = []
    try:
        comments = Comment.query.filter(Comment.article_id == article_id, Comment.status == 0
                                        ).order_by(
            Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comment_list = []
    for item in comments:
        comment_dict = item.to_dict()
        comment_list.append(comment_dict)

    data = {
        'user_info': user.to_dict() if user else None,
        "article": article.to_dict(),
        'categories': categories,
        'article_list':article_list,
        # "user_info": g.user.to_dict() if g.user else None,
        "click_articles_list": click_articles_list,
        "comments": comment_list
    }
    return render_template('blogs/detail.html', data=data)


@home.route('/comment/add', methods=['POST'])
@user_login_data
def add_comment():
    user = g.user
    if not user:
        return ParameterException(msg="用户未登录")
    article_id = request.json.get("article_id", None)
    content = request.json.get("content", None)
    parent_id = request.json.get("parent_id", None)
    if not all([article_id, content]):
        return ParameterException(msg="参数错误")
    article = Articles.query.get(article_id)
    if not article:
        return ParameterException(msg="文章不存在")

    comment = Comment()
    comment.content = content
    comment.user_id = user.id
    comment.article_id = article_id
    if parent_id:
        comment.parent_id = parent_id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return UnknownException()
    return Success(msg='ok', data=comment.to_dict())
