class NxosException(Exception):
    pass


class ProbeError(NxosException):
    pass


class RequestError(NxosException):
    """ retains any exception at time of making the command request """
    pass


class NoRespError(NxosException):
    """ indicates that the response does not have a results code """
    pass


class CommandError(NxosException):
    """ indicates the response code != 200 """
    pass
