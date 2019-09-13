from flask import render_template, current_app, request, abort, g

from web.model.model import Category, Articles
from web.utils.decorators import admin_required
from web.utils import constants
from web.exception import UnknownException, ParameterException, Success
from . import article


@article.route('/list')
def articles():
    cid = request.args.get("cid", 1)  # 分类标识
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", constants.ADMIN_NEWS_PAGE_MAX_COUNT)
    try:
        cid = int(cid)
        per_page = int(per_page)
        page = int(page)
    except (TypeError, ValueError) as e:
        current_app.logger.error(e)
        return ParameterException()
    filters = []
    if cid != 1:
        filters.append(Articles.category_id == cid)
    try:
        paginate = Articles.query.filter(*filters).order_by(Articles.create_time.desc()) \
            .paginate(page, per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()
    data = {
        "total_pages": paginate.pages,
        "current_page": paginate.page,
        "article_list": [paginate_article.to_base_dict() for paginate_article in paginate.items]
    }
    return Success(data=data)


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


@article.route('/detail/<int:article_id>')
def article_detail(article_id):
    try:
        article_res = Articles.query.get(article_id)
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()

    if not article_res:
        # 返回数据未找到的页面
        abort(404)

    article_res.clicks += 1
    # article_list = None
    try:
        article_list = Articles.query.order_by(Articles.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return UnknownException()

    click_articles_list = []
    for article_click in article_list if article_list else []:
        click_articles_list.append(article_click.to_basic_dict())

    data = {
        "article": article_res.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "click_articles_list": click_articles_list,
    }
    return render_template('blogs/detail.html', data=data)
    pass
