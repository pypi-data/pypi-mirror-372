__all__ = ['FsrApiException',
           'FsrApiRequestException',
           'FsrApiResponseException',]


# -- IMPORTS --

# -- Standard libraries --

# -- 3rd party libraries --

# -- Internal libraries --


class FsrApiException(Exception):
    """
    Base class all FS Register API exceptions.
    """
    ...


class FsrApiRequestException(FsrApiException):
    """
    Base class all FS Register API request exceptions.
    """
    ...


class FsrApiResponseException(FsrApiException):
    """
    Base class all FS Register API response exceptions.
    """
    ...
