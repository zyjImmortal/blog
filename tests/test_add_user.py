from web import create_app, db
from web.model.model import User


def main():
    app = create_app("dev")
    with app.app_context():
        user = User()
        user.nick_name = "admin"
        user.password = "123456"
        user.email = '1234995678@qq.com'
        user.is_admin = True
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

if __name__ == '__main__':
    main()
