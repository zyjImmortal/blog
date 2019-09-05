from . import article


@article.route('/list')
def articles():
    pass


@article.route('/add',methods=['POST'])
def add_article():
    pass