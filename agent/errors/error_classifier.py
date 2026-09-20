from __future__ import annotations

from enum import Enum

from .exceptions import (
    TransientError,
    PermanentError,
)


class ErrorType(str, Enum):

    TRANSIENT = "transient" 
    PERMANENT = "permanent" 
    UNKNOWN = "unknown"



class ErrorClassifier:
    """ 
    Classifies exceptions based on whether retrying 
    the failed operation is likely to succeed. 
    """

    _TRANSIENT_STATUS_CODES = { 
        408,
        429, 
        500, 
        502, 
        503, 
        504,
    }

    _PERMANENT_STATUS_CODES = { 
        400, 
        401, 
        403, 
        404, 
        409, 
        422,
    }

    @classmethod
    def classify(cls, error: Exception) -> ErrorType:
        """ 
        Classify an exception as transient, permanent, or unknown.
        """

        if isinstance(error, TransientError):
            return ErrorType.TRANSIENT

        if isinstance(error, PermanentError):
            return ErrorType.PERMANENT

        status_code = getattr(error, "status_code", None)

        if status_code in cls._TRANSIENT_STATUS_CODES:
            return ErrorType.TRANSIENT

        if status_code in cls._PERMANENT_STATUS_CODES:
            return ErrorType.PERMANENT

        return ErrorType.UNKNOWN
