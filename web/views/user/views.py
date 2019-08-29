from . import user


@user.register('/register', methods=['POST'])
def register():
    pass


@user.register('/image_code', methods=['POST'])
def get_image_code():
    pass


@user.register('/email_code', methods=['POST'])
def get_email_code():
    pass


@user.register('/login', methods=['POST'])
def login():
    pass
