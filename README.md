# blog
## 项目初始化
* 安装python3.6以上环境
* 安装pipenv
* 项目根目录下执行pipenv install
* 执行pipenv shell激活虚拟环境
* 项目根目录下新建logs文件夹
* 执行python manage.py db init 初始化数据迁移文件
* 在项目根目录下执行python manage.py db migrate,生成数据库迁移
* 执行python manage.py db upgrade 同步迁移数据到数据库
* 执行python manage.py runserver 启动服务
*  ```gunicorn -w 2 -b 127.0.0.1:5000 manage:app```

## 项目说明
### 所用的库
