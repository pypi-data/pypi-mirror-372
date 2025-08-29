"""
Exceptions raised by the object clerk
"""

import logging

from pydantic import BaseModel
from tenacity import Retrying
from tenacity import after_log
from tenacity import before_log
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import stop_never
from tenacity import wait_exponential_jitter

logger = logging.getLogger(__name__)


class ObjectClerkException(Exception):
    """
    Base Exception for the object clerk
    """


class ObjectClerkServerInternalException(ObjectClerkException):
    """
    Exception raised when the connected server raises a retry-able
    e.g. 503 error
    """


class ObjectClerkServerAuthException(ObjectClerkException):
    """
    Exception raised when the connected server raises an
    authorization or authentication exception e.g. 401 or 403
    """


class ObjectNotFoundException(ObjectClerkException):
    """
    Exception when an object cannot be found either due to bucket or object key validity
    """


class ObjectVerificationException(ObjectClerkException):
    """
    Exception when checksums of source and destination data mismatch
    """


class ObjectSaveException(ObjectClerkException):
    """
    Exception when objects cannot be saved due to size or readability
    """


class RetryerFactory(BaseModel):
    """
    Translator for the retry configuration to a tenacity.Retrying object.

    >>> from object_clerk.exceptions import RetryerFactory
    >>> factory = RetryerFactory()
    >>> retryer = factory()
    """

    delay_min: float = 1.0
    delay_max: float = 300.0
    backoff: float = 2.0
    jitter_min: float = 0
    jitter_max: float = 10.0
    attempts: int = -1  # -1 means retry forever
    exceptions: type[Exception] | tuple[type[Exception], ...] = type(
        Exception
    )  # retry any exception

    def __call__(self) -> Retrying:
        """
        Returns a tenacity.Retrying object based on the configuration.
        """
        wait = wait_exponential_jitter(
            initial=self.delay_min,
            max=self.delay_max,
            exp_base=self.backoff,
            jitter=self.jitter_max,
        )

        stop = stop_never
        if self.attempts > -1:
            stop = stop_after_attempt(self.attempts)
        return Retrying(
            retry=retry_if_exception_type(self.exceptions),
            wait=wait,
            stop=stop,
            before=before_log(logger=logger, log_level=logging.DEBUG),
            after=after_log(logger=logger, log_level=logging.DEBUG),
        )
