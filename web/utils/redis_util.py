from flask import current_app
import redis

from . import constants


class RedisUtil:

    @staticmethod
    def _get_conn():
        host = current_app.config['REDIS_HOST']
        port = current_app.config['REDIS_PORT']
        db = current_app.config['REDIS_DB']
        return redis.StrictRedis(host=host, port=port, db=db)

    @classmethod
    def set(cls, key, value, expire=None):
        if expire:
            expire_in_seconds = expire
        else:
            expire_in_seconds = constants.IMAGE_CODE_REDIS_EXPIRES
        c = cls._get_conn()
        c.set(key, value, ex=expire_in_seconds)

    @classmethod
    def get(cls, key):
        c = cls._get_conn()
        return c.get(key)

    @classmethod
    def hset(cls, name, key, value):
        c = cls._get_conn()
        c.hset(name, key, value)

    @classmethod
    def hget(cls, name, key):
        c = cls._get_conn()
        return c.hget(name, key)
