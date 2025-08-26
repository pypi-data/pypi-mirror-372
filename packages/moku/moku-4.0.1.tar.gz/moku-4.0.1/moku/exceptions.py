class MokuException(Exception):
    """
    Base class for other Exceptions
    """

    pass


class StreamException(MokuException):
    """
    Error occurred while streaming the data
    """

    pass


class MokuNotFound(MokuException):
    """
    Unable to find Moku with given name/serial.
    """

    pass


class IncompatibleMokuException(Exception):
    """
    Base class for other Exceptions
    """

    pass


class IncompatiblePackageException(Exception):
    """
    Version of Client pakage is older then the version it is talking to
    """

    pass


class NoPlatformBitstream(MokuException):
    """
    Cannot find platform bitstream
    """

    pass


class NoInstrumentBitstream(MokuException):
    """
    Cannot find Instrument bitstream
    """

    pass


class NetworkError(MokuException):
    """
    Unexpected network error occurred
    """

    pass


class DeployException(MokuException):
    """
    Couldn't start instrument. Moku may not be licenced to use that instrument
    """

    pass


class OperationNotFound(MokuException):
    """
    Couldn't find valid function. May be due to incompatible versions
    """

    pass


class InvalidParameterException(MokuException):
    """
    Invalid parameter type or value for this operation
    """

    pass


class InvalidRequestException(MokuException):
    """
    A request for an invalid instrument configuration has been made.
    """

    pass


class UnexpectedChangeError(MokuException):
    """
    A request has been made for data but none will be generated
    """

    pass


class NoDataException(MokuException):
    """
    A request has been made for data but none will be generated
    """

    pass


class InvalidParameterRange(MokuException):
    """
    Parameter value is not one of the allowed values
    """

    pass
