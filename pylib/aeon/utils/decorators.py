# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import time

__all__ = ['decorators']


def retry(exceptions=(Exception,), timeout=120.0, polling_interval=5.0,
                init_delay=0.0, logger=None):
    """
    Keep trying running a given function until timeout occurs. After that,
    it will call the function one last time in order to re-throw the exception
    to the caller.

    @retry(timeout=10.0)
    def test():
        assert 1==0, "Math is working"

    you can also pass a tuple of exceptions to masquerade, e.g.:

    @retry(exceptions=(AssertionError, ValueError), timeout=10):
    def test():
        assert 1==0, "Math is working"


    Args:
        exceptions (tuple(Exception): single exception or tuple of exceptions to
            masquerade
        timeout (float): amount of time to retry [seconds]
        polling_interval (float): sleep time between retries [seconds]
        init_delay (float): initial delay before the retry loop [seconds]
        logger (logging.Logger): logger to use. If None, use print instead.
    """
    def wrapper(f):
        def wrapped(*args, **kwargs):
            time.sleep(init_delay)
            t0 = time.time()
            while time.time() < t0 + timeout:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), polling_interval)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg

                time.sleep(polling_interval)
            return f(*args, **kwargs)
        return wrapped
    return wrapper
