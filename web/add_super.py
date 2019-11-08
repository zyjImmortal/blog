from web import create_app, db
from web.model.model import User


def main():
    app = create_app('pro')
    with app.app_context():
        # 创建一个超级管理员
        user = User()
        user.nick_name = 'super'
        user.password = '123456'
        user.email = '1234995678@qq.com'
        user.admin = True
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    try:
        main()
        print("新增超级管理员成功")
    except Exception as e:
        raise e
