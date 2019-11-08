from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from web import create_app, db
import os

app = create_app('pro')
# docker run  --publish 443:443 --publish 80:80 --publish 22:22 --name gitlab --volume /home/dc2-user/worksapce/docker/gitlab/config:/etc/gitlab
# --volume /home/dc2-user/worksapce/docker/gitlab/logs:/var/log/gitlab  --volume /home/dc2-user/worksapce/docker/gitlab/data:/var/opt/gitlab gitlab/gitlab-ce

def main():
    manager = Manager(app)
    Migrate(app, db)  # 关联APP和db
    manager.add_command('db', MigrateCommand)

    manager.run()


if __name__ == '__main__':
    main()
