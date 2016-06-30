
from aeon import exceptions
from aeon.utils.probe import probe
from aeon.cumulus.connector import Connector


__all__ = ['Device']

class Device(object):
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
        got_ver = self.api.execute('show version')

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
            got_host = self.api.execute('show hostname')
            facts['fqdn'] = got_host.get('fqdn')
            facts['hostname'] = got_host.get('hostname')
        except:
            facts['fqdn'] = 'localhost'
            facts['hostname'] = 'localhost'

        facts['virtual'] = False    # TODO: need to check for this


