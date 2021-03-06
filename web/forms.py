from flask import request
from wtforms import Form as WTForm, PasswordField, StringField
from wtforms.validators import DataRequired, Regexp, length

from web.exception import ParameterException


class Form(WTForm):
    def __init__(self):
        data = request.get_json()
        args = request.args.to_dict()
        form_data = request.form
        super(Form, self).__init__(formdata=form_data, data=data, **args)

    def validate_for_api(self):
        # validate() 返回Boolean值
        valid = super(Form, self).validate()
        if not valid:
            return ParameterException(msg=self.errors)
        return self

class AddUserForm(Form):
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Regexp(r'^[0-9a-zA-Z]{6,22}$', message="密码长度必须在6~22位之间，包含字符、数字和_")])
    nick_name = StringField('昵称', validators=[
        DataRequired('昵称不能为空'),
        # Regexp(r''),
        length(min=2, max=10, message="昵称长度必须在2-10之间")
    ])
    email = StringField('邮箱', validators=[
        DataRequired('邮箱不能为空'),
        Regexp(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', message='电子邮箱不符合规范，请输入正确的邮箱')
    ])



class RegisterForm(Form):
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Regexp(r'^[0-9a-zA-Z]{6,22}$', message="密码长度必须在6~22位之间，包含字符、数字和_")])
    nick_name = StringField('昵称', validators=[
        DataRequired('昵称不能为空'),
        # Regexp(r''),
        length(min=2, max=10, message="昵称长度必须在2-10之间")
    ])
    email = StringField('邮箱', validators=[
        DataRequired('邮箱不能为空'),
        Regexp(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$', message='电子邮箱不符合规范，请输入正确的邮箱')
    ])


class CmsLoginForm(Form):
    password = PasswordField('密码', validators=[
        DataRequired('密码不能为空'),
        Regexp(r'^[0-9a-zA-Z]{6,22}$', message="密码长度必须在6~22位之间，包含字符、数字和_")])
    nick_name = StringField('昵称', validators=[
        DataRequired('昵称不能为空'),
        # Regexp(r''),
        length(min=2, max=10, message="昵称长度必须在2-10之间")
    ])


class CreateOrUpdateArticleForm(Form):
    title = StringField('标题', validators=[
        DataRequired('标题不能为空'),
        length(min=2, max=50, message="标题长度必须在2-50之间")
    ])
    digest = StringField('摘要', validators=[
        DataRequired("摘要不能为空"),
        length(min=20, max=50)
    ])
    pass


class CreateOrUpdateCommentForm(Form):
    pass


class CreateOrUpdateCategoryForm(Form):
    pass
