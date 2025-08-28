class UnavailableFilesystem(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def getMessageFromException(e):
    if hasattr(e, "message") and len(e.message) > 0:
        return e.message
    elif len(str(e)) > 0:
        return str(e)
    elif len(e.__class__.__name__) > 0:
        return e.__class__.__name__
    else:
        return "Exception"


class InvalidAPIUsage(Exception):
    """Exception for various API errors"""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["status_code"] = self.status_code
        return rv


class InternalError(Exception):
    """Exception for internal error"""

    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["status_code"] = self.status_code
        return rv
