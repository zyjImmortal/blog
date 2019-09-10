from flask import Blueprint

aux = Blueprint('aux', __name__, url_prefix='/aux')

from . import views
