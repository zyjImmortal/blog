from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from web import create_app, db

app = create_app("ivwen")


def main():
    manager = Manager(app)
    Migrate(app, db)  # 关联APP和db
    manager.add_command('db', MigrateCommand)

    manager.run()


if __name__ == '__main__':
    main()
