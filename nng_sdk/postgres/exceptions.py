class NngPostgresException(Exception):
    pass


class ItemNotFoundException(NngPostgresException):
    pass


class ItemAlreadyExistsException(NngPostgresException):
    pass


class UserDoesNotExist(NngPostgresException):
    pass
