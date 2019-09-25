from flask import render_template, current_app, request, abort, g

from web import db
from web.model.model import Category, Articles
from web.utils.decorators import admin_required
from web.utils import constants
from web.exception import UnknownException, ParameterException, Success
from web.utils.file_util import storage
from . import article
import traceback


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
        current_app.logger.error(traceback.format_exc())
        return ParameterException()
    filters = [Articles.status == 0]
    if cid != 1:
        filters.append(Articles.category_id == cid)
    try:
        paginate = Articles.query.filter(*filters).order_by(Articles.create_time.desc()) \
            .paginate(page, per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    data = {
        "total_pages": paginate.pages,
        "current_page": paginate.page,
        "article_list": [paginate_article.to_basic_dict() for paginate_article in paginate.items]
    }
    return Success(data=data)


@article.route('/add', methods=['POST', 'GET'])
@admin_required
def add_article():
    if request.method == "POST":
        title = request.form.get("title")
        source = "博主发布"
        digest = request.form.get("digest")
        content = request.form.get("content-html")
        content_md = request.form.get("content-markdown")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")
        if not all([title, source, digest, content, index_image, category_id, content_md]):
            return ParameterException(msg="参数错误")
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return ParameterException(msg="文件读取错误")
        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return ParameterException(msg="文件上传错误")
        article = Articles()
        article.title = title
        article.digest = digest
        article.content = content
        article.content_md = content_md
        article.category_id = category_id
        article.source = source
        article.user_id = g.user.id
        article.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        try:
            db.session.add(article)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            db.session.rollback()
            return UnknownException()
        return Success(msg="添加成功")
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
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
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    # TODO 最新分类不返回
    try:
        categories = Category.query.filter_by().all()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    if not article_res:
        # 返回数据未找到的页面
        abort(404)

    article_res.clicks += 1
    # article_list = None
    try:
        article_list = Articles.query.order_by(Articles.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    click_articles_list = []
    for article_click in article_list if article_list else []:
        click_articles_list.append(article_click.to_basic_dict())

    data = {
        "article": article_res.to_dict(),
        "categories": categories,
        # "user_info": g.user.to_dict() if g.user else None,
        "click_articles_list": click_articles_list,
    }
    return render_template('admin/news_edit_detail.html', data=data)


@article.route('/delete/<int:article_id>')
def delete_article(article_id):
    try:
        article_res = Articles.query.get(article_id)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    if not article_res:
        return ParameterException(msg="文章id不存在")
    article_res.status = 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()
    return Success(msg='删除成功')

@admin_required
@article.route('/edit', methods=["POST"])
def edit_article():
    article_id = request.form.get("article_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content-html")
    content_md = request.form.get("content-markdown")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    if not all([title, digest, content, category_id, content_md]):
        return ParameterException(msg="参数错误")
    try:
        article = Articles.query.get(article_id)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return UnknownException()

    if not article:
        return ParameterException(msg="文章不存在")
    key = ''
    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return ParameterException(msg="文件读取错误")

        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            return ParameterException(msg="文件上传错误")
        article.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    article.title = title
    article.digest = digest
    article.content = content
    article.content_md = content_md
    article.category_id = category_id
    # article.user_id = g.user.id

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return UnknownException()
    return Success(msg="编辑成功")

