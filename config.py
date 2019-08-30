import logging

from redis import StrictRedis


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+cymysql://zhouyajun:12345678@localhost:3306/article"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    SESSION_USE_SIGNER = True  # 指定开启签名
    SESSION_PERMANENT = False  # 默认永久不过期，需要设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USERNAME = 'zyj866955@163.com'
    MAIL_PASSWORD = 'zyj866955'
    MAIL_SUBJECT_PREFIX = '南极仙翁'
    SECRET_KEY = "jinwenjun"


class Dev(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class Pro(Config):
    LOG_LEVEL = logging.INFO


config = {
    'dev': Dev,
    'pro': Pro
}
