"""Circuit breaker can be used to interact with network resources.

If resources are known to crash the circuit breaker will wait before attempting
to use the resource again.
"""

import logging
import time

logger = logging.getLogger()


class CircuitBreaker(object):
    def __init__(self, retries, timeout, func):
        self.retries = retries
        self.timeout = timeout
        self.func = func

    def safe_call(self, *args):
        for i in range(0, self.retries):
            try:
                return self.func(*args)
            except Exception as e:
                logger.warning(f"Failed to use network resource, retry number {i}")
                if i == self.retries - 1:
                    raise e
                time.sleep(self.timeout)
