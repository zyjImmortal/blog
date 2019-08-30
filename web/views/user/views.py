from . import user


@user.route('/register', methods=['POST'])
def register():
    pass


@user.route('/image_code', methods=['POST'])
def get_image_code():
    pass


@user.route('/email_code', methods=['POST'])
def get_email_code():
    pass


@user.route('/login', methods=['POST'])
def login():
    pass
