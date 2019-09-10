from flask import request
from . import aux


@aux.route('/')
def tool():
    pass

@aux.route('/base64',methods=['POST'])
def base64():
    pass

@aux.route('/json',methods=["POST"])
def json():
    pass

@aux.route('/urlencode',methods=['POST'])
def url_encode():
    pass