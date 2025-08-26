

class BadResponseException(Exception):

    def __init__(self, status_code, reason, url, method=None, *args):
        message = "Bad response to URL: {} in {} method [status_code: {}, reason: {}]".format(url, method, status_code,
                                                                                              reason)
        super(BadResponseException, self).__init__(message)


class AuthException(BadResponseException):
    pass
