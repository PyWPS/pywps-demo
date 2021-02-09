class PyWPSError(Exception):
    """Exception class from which every exception in this library will derive.
         It enables other projects using this library to catch all errors coming
         from the library with a single "except" statement
    """
    pass


class BadUserInputError(PyWPSError):
    """A specific error"""
    pass
