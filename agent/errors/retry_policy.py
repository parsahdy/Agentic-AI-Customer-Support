from __future__ import annotations

import random
from dataclasses import dataclass

from .classifier import ErrorClassifier, ErrorType



@dataclass(frozen=True)
class RetryPolicy:
    """
    Defines retry behavior for transient failures.
    """

    max_retries: int = 3
    initial_delay: float = 1.0 
    max_delay: float = 30.0 
    backoff_factor: float = 2.0 
    jitter: float = 0.2


    def __post_init__(self):

        if self.max_retries < 0: 
            raise ValueError("max_retries cannot be negative.") 

        if self.initial_delay < 0: 
            raise ValueError("initial_delay cannot be negative.") 

        if self.max_delay < 0: 
            raise ValueError("max_delay cannot be negative.") 

        if self.backoff_factor < 1: 
            raise ValueError("backoff_factor must be greater than or equal to 1.") 

        if self.jitter < 0: 
            raise ValueError("jitter cannot be negative.")


    def should_retry(self, error: Exception,
                     retry_count: int) -> bool:

        """ 
        Decide whether the failed operation should be retried.
          
        retry_count represents how many retries have already happened.
        """

        error_type = ErrorClassifier.classify(error)

        if error_type != ErrorType.TRANSIENT:
            return False

        return retry_count < self.max_retries


    def get_delay(self, retry_count: int) -> float:
        """ 
        Calculate the delay before the next retry.
         
        retry_count: 
        1 -> first retry 
        2 -> second retry 
        3 -> third retry 
        """

        if retry_count <= 0: 
            raise ValueError("retry_count must be greater than zero.")

        base_delay = (self.initial_delay * (self.backoff_factor **(retry_count -1)))

        capped_delay = min(base_delay, self.max_delay)

        jitter_range = capped_delay * self.jitter

        if jitter_range == 0:
            return capped_delay

        return min(self.max_delay, 
                   capped_delay + random.uniform(-jitter_range, jitter_range))
