# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula


from aeon.eos.connector import Connector
from aeon.base.device import BaseDevice


__all__ = ['Device']


class Device(BaseDevice):
    OS_NAME = 'eos'

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        BaseDevice.__init__(self, target, Connector, **kwargs)

    def gather_facts(self):

        facts = self.facts
        got_ver = self.api.execute('show version')

        facts['vendor'] = 'arista'
        facts['os_name'] = self.OS_NAME
        facts['os_version'] = got_ver['version']
        facts['hw_model'] = got_ver['modelName']
        facts['hw_version'] = got_ver['hardwareRevision']
        facts['hw_part_number'] = None
        facts['hw_part_version'] = None
        facts['chassis_id'] = None
        facts['mac_address'] = got_ver['systemMacAddress']

        facts['virtual'] = bool('vEOS' == facts['hw_model'])

        if facts['virtual']:
            got_ma1 = self.api.execute('show interfaces ma1')
            macaddr = got_ma1['interfaces']['Management1']['physicalAddress']
            facts['serial_number'] = macaddr.replace(':', '').upper()
        else:
            facts['serial_number'] = got_ver['serialNumber']

        try:
            got_host = self.api.execute('show hostname')
            facts['fqdn'] = got_host.get('fqdn')
            facts['hostname'] = got_host.get('hostname')
        except:  # NOQA
            facts['fqdn'] = 'localhost'
            facts['hostname'] = 'localhost'
