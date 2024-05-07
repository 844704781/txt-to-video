class ConfigParser:

    def __init__(self, username, password):
        if username is None or username == '' \
                or password is None or password == '':
            raise Exception("账号密码无效")

        self._username = username
        self._password = password

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password
