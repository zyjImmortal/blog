from flask import render_template, session, current_app

from web.exception import Success, UnknownException
from web.model.model import User, Articles
from . import home


@home.route('/')
def index():
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            user = User.query.get(id=user_id)
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
    info = {
        'user_info': user.to_dict() if user else None,
        'articles_info': articles_info
    }
    return render_template('blogs/index.html', info=info)

