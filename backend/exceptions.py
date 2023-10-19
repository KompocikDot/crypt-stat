class MissingDBUrlException(BaseException):
    """Database url (DB_URL) was not found in .env"""


class DbConnectionException(BaseException):
    """Could not initialize connection to the db"""


class InvalidDataChartType(BaseException):
    """Could not find a data with given type"""
