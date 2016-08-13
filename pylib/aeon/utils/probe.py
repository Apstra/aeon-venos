# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import socket
import datetime
import time

__all__ = ['probe']


def probe(target, port=None, protocol=None, timeout=5, interval=1):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(seconds=timeout)

    port = port or socket.getservbyname(protocol)

    while datetime.datetime.now() < end:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(interval)
        try:
            s.connect((target, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            elapsed = datetime.datetime.now() - start
            return True, elapsed
        except:
            time.sleep(interval)
            pass

    elapsed = datetime.datetime.now() - start
    return False, elapsed.seconds
