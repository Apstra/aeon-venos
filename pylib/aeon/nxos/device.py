# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula


from functools import partial
import importlib

from aeon.base.device import BaseDevice
from aeon.nxos.connector import NxosConnector as Connector


__all__ = ['Device']


class Device(BaseDevice):
    OS_NAME = 'nxos'

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        BaseDevice.__init__(self, target, Connector, **kwargs)

    def close(self):
        # nothing to do for close at this time, yo!
        pass

    def gather_facts(self):
        exec_show = partial(self.api.exec_opcmd, resp_fmt='json')

        facts = self.facts
        facts['os_name'] = self.OS_NAME

        got = exec_show('show hostname')
        facts['fqdn'] = got['hostname']
        facts['hostname'], _, facts['domain_name'] = facts['fqdn'].partition('.')

        attempts = 1
        while attempts < 5:
            try:
                got = exec_show('show hardware')
            except:  # NOQA
                attempts -= 1
            else:
                break

        facts['os_version'] = got['kickstart_ver_str']
        facts['chassis_id'] = got['chassis_id']
        facts['virtual'] = bool('NX-OSv' in facts['chassis_id'])

        row = got['TABLE_slot']['ROW_slot']['TABLE_slot_info']['ROW_slot_info'][0]
        facts['serial_number'] = row['serial_num']
        facts['hw_model'] = row['model_num']
        facts['hw_part_number'] = row['part_num']
        facts['hw_part_version'] = row['part_revision']
        facts['hw_version'] = row['hw_ver']

        got = exec_show('show interface mgmt0')
        raw_mac = got['TABLE_interface']['ROW_interface']['eth_hw_addr'].replace('.', '')
        facts['mac_address'] = ':'.join(s.encode('hex') for s in raw_mac.decode('hex'))

    def __getattr__(self, item):
        # ##
        # ## this is rather perhaps being a bit "too clever", but I sometimes
        # ## can't help myself ;-P
        # ##

        # if the named addon module does not exist, this will raise
        # an ImportError.  We might want to catch this and handle differently

        mod = importlib.import_module('.autoload.%s' % item, package=__package__)

        def wrapper(*vargs, **kvargs):
            cls = getattr(mod, '_%s' % item)
            self.__dict__[item] = cls(self, *vargs, **kvargs)

        return wrapper
