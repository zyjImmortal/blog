import logging

from redis import StrictRedis


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+cymysql://zhouyajun:12345678@localhost:3306/blog"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    SESSION_TYPE = 'redis'
    # decode_responses=True，写入的键值对中的value为str类型，不加这个参数写入的则为字节类型。
    # StrictRedis(host=config[config_name].REDIS_HOST,
    #                               port=config[config_name].REDIS_PORT, decode_responses=True)
    #  这个地方不要多余的加decode_responses=True，不然会报编码错误
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 指定开启签名
    SESSION_PERMANENT = False  # 默认永久不过期，需要设置过期时间
    SESSION_KEY_PREFIX = "session:"
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USERNAME = 'zyj866955@163.com'
    MAIL_PASSWORD = 'zyj866955'
    MAIL_SUBJECT_PREFIX = '南极仙翁'
    SECRET_KEY = "jinwenjun"
    JSON_AS_ASCII = False

    # 文章点击排行榜数量限制
    TOP_CLICK_COUNTS = 7


class Dev(Config):
    DEBUG = True
    # LOG_LEVEL = logging.DEBUG


class Pro(Config):
    LOG_LEVEL = logging.INFO


config = {
    'dev': Dev,
    'pro': Pro
}

