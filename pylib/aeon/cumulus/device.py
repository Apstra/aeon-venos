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

    def gather_facts(self):

        facts = self.facts
        facts['os_name'] = self.OS_NAME

        good, got = self.api.execute([
            'hostname',
            'sudo decode-syseeprom',
            'cat /etc/lsb-release | grep RELEASE | cut -d= -f2'
        ])

        if not good:
            raise exceptions.CommandError(commands=got)

        facts['fqdn'] = got[0]['stdout'].strip()
        facts['hostname'] = facts['fqdn']

        decode = got[1]['stdout']
        scanner = re.compile(r'(.+) 0x[A-F0-9]{2}\s+\d+(.+)')
        gathered = {
            tag.strip(): value
            for tag, value in scanner.findall(decode)}

        facts['vendor'] = gathered['Vendor Name']
        facts['serial_number'] = gathered['Serial Number']
        facts['hw_model'] = gathered['Product Name']
        facts['hw_part_number'] = gathered['Part Number']
        facts['hw_version'] = gathered['Label Revision']
        facts['service_tag'] = gathered['Service Tag']
        facts['virtual'] = False    # TODO: need to check for this

        facts['os_version'] = got[2]['stdout'].strip()
