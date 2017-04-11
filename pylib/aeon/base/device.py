# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import socket
import datetime
import time

from aeon.exceptions import ProbeError


class BaseDevice(object):
    DEFAULT_PROBE_TIMEOUT = 3

    def __init__(self, target, connector, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        self.target = target
        self.port = None
        self.user = kwargs.get('user', 'admin')
        self.passwd = kwargs.get('passwd', 'admin')
        self.facts = {}
        self.api = connector(hostname=target, user=self.user, passwd=self.passwd)

        if 'no_probe' not in kwargs:
            self.probe()

        if 'no_gather_facts' not in kwargs:
            self.gather_facts()

    def gather_facts(self):
        """
        Will be overridden by subclass
        :return: None
        """
        pass

    def probe(self):
        interval = 1
        timeout = self.DEFAULT_PROBE_TIMEOUT
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=timeout)

        port = self.port or socket.getservbyname(self.api.proto)

        while datetime.datetime.now() < end:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(interval)
            try:
                s.connect((self.target, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                elapsed = datetime.datetime.now() - start
                return True, elapsed
            except:
                time.sleep(interval)
                pass
        # Raise ProbeError if unable to reach in time allotted
        raise ProbeError('Unable to reach device within %s seconds' % timeout)

    def __repr__(self):
        return 'Device(%r)' % self.target

    def __str__(self):
        return '{vendor} {os} at {target}'.format(vendor=self.facts['vendor'],
                                                  os=self.facts['os'],
                                                  target=self.target)
