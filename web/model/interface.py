from web import db


class BaseCrud(db.Model):
    # 告诉sqlalchemy 这个类是一个基类，不用创建表
    __abstract__ = True

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 硬删除
    def delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        if one:
            return cls.query.filter_by(**kwargs).first()
        # offset指定从那个位置开始查，limit指定数量，all返回数据
        return cls.query.filter_by(**kwargs).offset(start).limit(count).all()

    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key, value in kwargs.items():
            if hasattr(one, key) and key != 'id':
                setattr(one, key, value)
        db.session.add(one)
        if kwargs.get("commit"):
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get("commit"):
            db.session.commit()
        return self
