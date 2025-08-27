class KToolException(Exception):
    pass


class UnsupportedData(KToolException):
    pass

class UnsupportedHTTPMethod(KToolException):
    pass