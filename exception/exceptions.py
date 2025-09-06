class NoAdminUser(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidRealm(Exception):
    def __init__(self, message):
        super().__init__(message)

