"""Decorators for tokenizer."""

import time

from metrics import Metrics


def monitor(func):
    """Decorator for monitoring the latency of a function."""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        stop = time.time()
        Metrics().FUNCTION_LATENCY.labels(func.__qualname__).observe(stop - start)
        return result

    return wrapper
