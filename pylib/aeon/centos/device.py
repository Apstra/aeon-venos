# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from aeon.base.device import BaseDevice
from aeon.cumulus.connector import Connector


__all__ = ['Device']


class Device(BaseDevice):
    OS_NAME = 'centos'

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        BaseDevice.__init__(self, target, Connector, **kwargs)

    def get_mac_address(self, link_name):
        good, got = self.api.execute(['/sbin/ip link show dev %s' % link_name])
        data = got[0]['stdout']
        macaddr = data.partition('link/ether ')[-1].split()[0]
        return macaddr.upper()

    def gather_facts(self):

        facts = self.facts
        facts['os_name'] = self.OS_NAME
        good, got = self.api.execute([
            'hostname',
            'cat /etc/centos-release | cut -d" " -f3'
        ])

        facts['fqdn'] = got[0]['stdout'].strip()
        facts['hostname'] = facts['fqdn']
        facts['os_version'] = got[1]['stdout'].strip()
        facts['virtual'] = None
        facts['vendor'] = 'CentOS'
        facts['serial_number'] = None
        facts['mac_address'] = self.get_mac_address("eth0")
        facts['hw_model'] = 'Server'
        facts['hw_part_number'] = None
        facts['hw_version'] = None
        facts['service_tag'] = None
