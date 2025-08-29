class WrongRequest(Exception):  # noqa N818
    """
    Created for cases when error caused not by error in service code, but by error in request
    Currently usage the only usage is config validation for document processors
    """


class ProcessorConfigError(WrongRequest):
    pass
