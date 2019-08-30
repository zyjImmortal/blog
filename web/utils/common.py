from flask import render_template, current_app
from flask_mail import Message, Mail

import random


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
