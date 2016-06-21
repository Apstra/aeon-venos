
from aeon import exceptions
from aeon.utils.probe import probe
from aeon.eos.connector import Connector


__all__ = ['Device']

class Device(object):
    DEFAULT_PROBE_TIMEOUT = 3

    def __init__(self, target, **kwargs):
        """
        :param target: hostname or ipaddr of target device
        :param kwargs:
            'user' : login user-name, defaults to "admin"
            'passwd': login password, defaults to "admin
        """
        self.target = target

        user = kwargs.get('user', 'admin')
        passwd = kwargs.get('passwd', 'admin')

        self.api = Connector(hostname=self.target, user=user, passwd=passwd)

        self.facts = {}

        if 'no_probe' not in kwargs:
            self.probe(**kwargs)

        if 'no_gather_facts' not in kwargs:
            self.gather_facts()

    def probe(self, **kwargs):
        timeout = kwargs.get('timeout') or self.DEFAULT_PROBE_TIMEOUT
        ok, elapsed = probe(self.target, protocol=self.api.proto, timeout=timeout)
        if not ok:
            raise exceptions.ProbeError()

    def gather_facts(self):

        facts = self.facts
        got_ver = self.api.execute('show version')['result'][0]

        facts['vendor'] = 'arista'
        facts['os'] = 'eos'
        facts['os_version'] = got_ver['version']
        facts['serial_number'] = got_ver['serialNumber']
        facts['hw_model'] = got_ver['modelName']
        facts['hw_version'] = got_ver['hardwareRevision']
        facts['hw_part_number'] = None
        facts['hw_part_version'] = None
        facts['chassis_id'] = None

        try:
            got_host = self.api.execute('show hostname').get('result')[0]
            facts['fqdn'] = got_host.get('fqdn')
            facts['hostname'] = got_host.get('hostname')
        except:
            facts['fqdn'] = 'localhost'
            facts['hostname'] = 'localhost'

        facts['virtual'] = False    # TODO: need to check for this


