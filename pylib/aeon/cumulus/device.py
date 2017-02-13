# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import re

from aeon import exceptions
from aeon.utils.probe import probe
from aeon.cumulus.connector import Connector


__all__ = ['Device']


class Device(object):
    OS_NAME = 'cumulus'
    DEFAULT_PROBE_TIMEOUT = 3
    DEFAULT_USER = 'admin'
    DEFAULT_PASSWD = 'admin'

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        self.target = target
        self.api = Connector(hostname=self.target,
                             user=kwargs.get('user', self.DEFAULT_USER),
                             passwd=kwargs.get('passwd', self.DEFAULT_PASSWD))

        self.facts = {}

        if 'no_probe' not in kwargs:
            self.probe(**kwargs)

        if 'no_gather_facts' not in kwargs:
            self.gather_facts()

    def probe(self, **kwargs):
        timeout = kwargs.get('timeout') or self.DEFAULT_PROBE_TIMEOUT
        ok, elapsed = probe(self.target, protocol='ssh', timeout=timeout)
        if not ok:
            raise exceptions.ProbeError()

    def _serial_from_link(self, link_name):
        good, got = self.api.execute(['ip link show dev %s' % link_name])
        data = got[0]['stdout']
        macaddr = data.partition('link/ether ')[-1].split()[0]
        return macaddr.replace(':', '').upper()

    def gather_facts(self):

        facts = self.facts
        facts['os_name'] = self.OS_NAME

        good, got = self.api.execute([
            'hostname',
            'cat /etc/lsb-release | grep RELEASE | cut -d= -f2',
            'test -e /usr/cumulus/bin/decode-syseeprom'
        ])

        facts['fqdn'] = got[0]['stdout'].strip()
        facts['hostname'] = facts['fqdn']
        facts['os_version'] = got[1]['stdout'].strip()
        virt2 = bool(0 != got[2]['exit_code'])

        if virt2 is True:
            # this is a Cumulus VX 2.x device
            facts['virtual'] = True
            facts['vendor'] = 'CUMULUS-NETWORKS'
            facts['serial_number'] = self._serial_from_link("eth0")
            facts['mac_address'] = self._serial_from_link("eth0")
            facts['hw_model'] = 'CUMULUS-VX'
            facts['hw_part_number'] = None
            facts['hw_version'] = None
            facts['service_tag'] = None
        else:
            good, got = self.api.execute([
                'sudo decode-syseeprom',
            ])

            syseeprom = got[0]['stdout']
            scanner = re.compile(r'(.+) 0x[A-F0-9]{2}\s+\d+\s+(.+)')
            decoded = {
                tag.strip(): value
                for tag, value in scanner.findall(syseeprom)}

            facts['mac_address'] = self._serial_from_link("eth0")
            facts['vendor'] = decoded.get('Vendor Name', 'no-vendor-name')
            facts['serial_number'] = decoded.get('Serial Number', 'no-serial-number')
            facts['hw_model'] = decoded.get('Product Name', 'no-product-name')
            facts['virtual'] = bool(facts['hw_model'] == 'VX')
            facts['hw_part_number'] = decoded.get('Part Number', 'no-part-number')
            facts['hw_version'] = decoded.get('Label Revision', 'no-hw-version')
            facts['service_tag'] = decoded.get('Service Tag', 'no-service-tag')
