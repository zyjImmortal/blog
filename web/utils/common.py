from flask import render_template, current_app, session
from flask_mail import Message, Mail

import random

from web.model.model import User


def random_email_code():
    return random.randint(0, 9999)


def send_mail(mail: Mail, to, subject, template, **kwargs):
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


def send_register_mail_code(mail: Mail, to_email_address, username, email_code):
    send_mail(mail, to_email_address, "邮箱注册验证码",
              'emails/sms', username=username, email_code=email_code)


def get_current_user():
    username = session.get("nick_name", None)
    password = session.get("password", None)
    if username and password:
        user = User.query.filter_by(nick_name=username).first()
        return user if user else None
    return None
