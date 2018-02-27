# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from aeon.base.device import BaseDevice
from aeon.cumulus.connector import Connector


__all__ = ['Device']


class Device(BaseDevice):
    OS_NAME = 'OPX'

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        BaseDevice.__init__(self, target, Connector, **kwargs)

    def get_mac_address(self):
        good, got = self.api.execute(['ip link show'])
        data = got[0]['stdout']
        macaddr = data.partition('link/ether ')[-1].split()[0]
        return macaddr.upper()

    def gather_facts(self):

        facts = self.facts
        facts['os_name'] = self.OS_NAME

        good, got = self.api.execute([
            'hostname',
            """grep -oP '^OS_VERSION="\K.*\d' /etc/OPX-release-version""",
            """grep -oP '^PLATFORM="\K.*\w' /etc/OPX-release-version"""
        ])

        facts['fqdn'] = got[0]['stdout'].strip()
        facts['hostname'] = facts['fqdn']
        facts['os_version'] = got[1]['stdout'].strip()
        facts['virtual'] = bool('vm' in got[2]['stdout'].lower())
        facts['vendor'] = 'OPX'
        facts['serial_number'] = self.get_mac_address().replace(':', '')
        facts['mac_address'] = self.get_mac_address()
        facts['hw_model'] = got[2]['stdout'].strip()
        facts['hw_part_number'] = None
        facts['hw_version'] = None
        facts['service_tag'] = None
