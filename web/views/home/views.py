from flask import render_template, session, current_app

from web.exception import Success, UnknownException
from web.model.model import User, Articles, Category
from web.utils import constants
from . import home


@home.route('/')
def index():
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return UnknownException()
    articles = []
    try:
        articles = Articles.query.order_by(Articles.clicks.desc()).limit(current_app.config['TOP_CLICK_COUNTS'])
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    articles_info = [article.to_dict() for article in articles]

    # 分类信息
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()

    try:
        article_list = Articles.query.order_by(Articles.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
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
    return render_template('blogs/index.html', info=info)
