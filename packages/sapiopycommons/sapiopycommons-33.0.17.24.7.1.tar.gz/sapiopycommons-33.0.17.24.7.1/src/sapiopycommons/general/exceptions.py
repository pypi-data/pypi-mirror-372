# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class SapioException(Exception):
    """
    A generic exception thrown by sapiopycommons methods. Typically caused by programmer error, but may also be from
    extremely edge case user errors. For expected user errors, use SapioUserErrorException.
    """
    pass


# CommonsWebhookHandler catches this exception and returns "User Cancelled."
class SapioUserCancelledException(SapioException):
    """
    An exception thrown when the user cancels a client callback.
    """
    pass


# CommonsWebhookHandler catches this exception and returns the text to the user as display text in a webhook result.
class SapioUserErrorException(SapioException):
    """
    An exception caused by user error (e.g. user provided a CSV when an XLSX was expected), which promises to return a
    user-friendly message explaining the error that should be displayed to the user. It is the responsibility of the
    programmer to catch any such exceptions and return the value in e.args[0] as text for the user to see (such as
    through the display text of a webhook result).
    """
    pass


# CommonsWebhookHandler catches this exception and returns the text in a display_error client callback.
class SapioCriticalErrorException(SapioException):
    """
    A critical exception caused by user error, which promises to return a user-friendly message explaining the error
    that should be displayed to the user. It is the responsibility of the programmer to catch any such exceptions and
    return the value in e.args[0] as text for the user to see (such as through a dialog form client callback request).
    """
    pass
