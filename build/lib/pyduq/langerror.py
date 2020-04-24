class Error(Exception):
    """
    Error: A generic extension of the Exception base class, used to form the basis
    of all LANG errors.
    """
    pass

class LangError(Error):
    """
    LangError: The LANG base class for an error. All LANG errors must
    extend this class.
    
    Attributes:
        expression -- expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class ValidationError(LangError):
    """
    ValidationError: An implementation of LangError specificlaly for handling lang validation errors.
    """
    def __init__(self, error, message):
        self.error = error
        self.message = message

        
