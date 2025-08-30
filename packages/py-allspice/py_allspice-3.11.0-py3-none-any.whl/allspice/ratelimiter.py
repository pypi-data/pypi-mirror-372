import time

import requests


class RateLimitedSession(requests.Session):
    """
    A requests.Session that is rate limited.

    :param max_calls: Maximum number of calls per period
    :param period: Time period in seconds

    Example:

        session = RateLimitedSession(max_calls=10, period=1)
        session.get("https://example.com") # Will be rate limited
    """

    max_calls: int
    period: float

    _calls: int
    _reset_time: float

    def __init__(self, max_calls, period=1.0):
        self.max_calls = max_calls
        self.period = period

        self._calls = 0
        self._reset_time = time.time()
        super().__init__()

    def request(self, *args, **kwargs):
        if time.time() - self._reset_time > self.period:
            self._calls = 0
            self._reset_time = time.time()

        if self._calls < self.max_calls:
            self._calls += 1
        else:
            time.sleep(self.period - (time.time() - self._reset_time))
            # Note that this is self.request, not super().request.
            return self.request(*args, **kwargs)

        return super().request(*args, **kwargs)
