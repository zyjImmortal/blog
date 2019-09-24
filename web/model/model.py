from datetime import datetime

from sqlalchemy import orm, inspect
from werkzeug.security import generate_password_hash, check_password_hash

from web.exception import NotFound, ParameterException, AuthFailed
from web.utils import constants
from web import db


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set([column.name for column in columns])
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


# 用户收藏表，建立用户与其收藏文章多对多的关系
tb_user_collection = db.Table(
    "blogs_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("blog_user.id"), primary_key=True),  # 文章编号
    db.Column("article_id", db.Integer, db.ForeignKey("blog_article.id"), primary_key=True),  # 分类编号
    db.Column("create_time", db.DateTime, default=datetime.now)  # 收藏创建时间
)

tb_user_follows = db.Table(
    "blogs_user_fans",
    db.Column('follower_id', db.Integer, db.ForeignKey('blog_user.id'), primary_key=True),  # 粉丝id
    db.Column('followed_id', db.Integer, db.ForeignKey('blog_user.id'), primary_key=True)  # 被关注人的id
)


class User(BaseModel, db.Model, MixinJSONSerializer):
    """用户"""
    __tablename__ = "blog_user"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    email = db.Column(db.String(64), unique=True, nullable=False)  # 手机号
    avatar_url = db.Column(db.String(256))  # 用户头像路径
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录时间
    is_admin = db.Column(db.Boolean, default=False)
    is_delete = db.Column(db.Boolean, default=False)
    signature = db.Column(db.String(512))  # 用户签名
    gender = db.Column(  # 订单的状态
        db.Enum(
            "MAN",  # 男
            "WOMAN"  # 女
        ),
        default="MAN")

    # 当前用户收藏的所有文章
    collection_articles = db.relationship("Articles", secondary=tb_user_collection, lazy="dynamic")  # 用户收藏的新闻
    # 用户所有的粉丝，添加了反向引用followed，代表用户都关注了哪些人
    followers = db.relationship('User',
                                secondary=tb_user_follows,
                                primaryjoin=id == tb_user_follows.c.followed_id,
                                secondaryjoin=id == tb_user_follows.c.follower_id,
                                backref=db.backref('followed', lazy='dynamic'),
                                lazy='dynamic')

    # 当前用户所发布的文章
    article_list = db.relationship('Articles', backref='user', lazy='dynamic')

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "avatar_url": constants.QINIU_DOMIN_PREFIX + self.avatar_url if self.avatar_url else "",
            "email": self.email,
            "gender": self.gender if self.gender else "MAN",
            "signature": self.signature if self.signature else "",
            "followers_count": self.followers.count(),
            "article_count": self.article_list.count()
        }
        return resp_dict

    def to_admin_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "role": "管理员" if self.is_admin else "游客",
            "email": self.email,
            "register": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict

    @classmethod
    def verify(cls, nickname, password):
        user = cls.query.filter_by(nick_name=nickname).first()
        if user is None:
            raise NotFound(msg='用户不存在')
        # if user is None or user.delete_time is not None:
        #     raise NotFound(msg='用户不存在')
        if not user.check_password(password):
            raise ParameterException(msg='密码错误，请输入正确密码')
        if not user.is_admin:
            raise AuthFailed(msg='您目前还不是管理员，请联系超级管理员开通权限')
        return user


class Articles(BaseModel, db.Model, MixinJSONSerializer):
    """文章"""
    __tablename__ = "blog_article"

    id = db.Column(db.Integer, primary_key=True)  # 文章编号
    title = db.Column(db.String(256), nullable=False)  # 文章标题
    source = db.Column(db.String(64), nullable=False)  # 文章来源
    digest = db.Column(db.String(512), nullable=False)  # 文章摘要
    content = db.Column(db.Text, nullable=False)  # 文章内容
    content_md = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0)  # 浏览量
    index_image_url = db.Column(db.String(256))  # 文章列表图片路径
    category_id = db.Column(db.Integer, db.ForeignKey("article_category.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("blog_user.id"))  # 当前文章的作者id
    status = db.Column(db.Integer, default=0)  # 当前文章状态 如果为0代表审核通过，1代表审核中，-1代表审核不通过
    reason = db.Column(db.String(256))  # 未通过原因，status = -1 的时候使用
    # 当前新闻的所有评论
    comments = db.relationship("Comment", lazy="dynamic")

    def to_review_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "reason": self.reason if self.reason else ""
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "index_image_url": self.index_image_url,
            "clicks": self.clicks,
        }
        return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "digest": self.digest,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "content_md": self.content_md,
            "comments_count": self.comments.count(),
            "clicks": self.clicks,
            "category": self.category.to_dict(),
            "index_image_url": self.index_image_url,
            "author": self.user.to_dict() if self.user else None
        }
        return resp_dict


class Comment(BaseModel, db.Model, MixinJSONSerializer):
    """评论"""
    __tablename__ = "article_comment"

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    user_id = db.Column(db.Integer, db.ForeignKey("blog_user.id"), nullable=False)  # 用户id
    article_id = db.Column(db.Integer, db.ForeignKey("blog_article.id"), nullable=False)  # 文章id
    content = db.Column(db.Text, nullable=False)  # 评论内容
    parent_id = db.Column(db.Integer, db.ForeignKey("article_comment.id"))  # 父评论id
    parent = db.relationship("Comment", remote_side=[id])  # 自关联
    like_count = db.Column(db.Integer, default=0)  # 点赞条数

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "parent": self.parent.to_dict() if self.parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "article_id": self.article_id,
            "like_count": self.like_count
        }
        return resp_dict


class CommentLike(BaseModel, db.Model, MixinJSONSerializer):
    """评论点赞"""
    __tablename__ = "article_comment_like"
    comment_id = db.Column("comment_id", db.Integer, db.ForeignKey("article_comment.id"), primary_key=True)  # 评论编号
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("blog_user.id"), primary_key=True)  # 用户编号


class Category(BaseModel, db.Model, MixinJSONSerializer):
    """文章分类"""
    __tablename__ = "article_category"

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    name = db.Column(db.String(64), nullable=False)  # 分类名
    news_list = db.relationship('Articles', backref='category', lazy='dynamic')

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name
        }
        return resp_dict
