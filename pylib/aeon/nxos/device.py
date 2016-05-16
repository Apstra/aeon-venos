
from functools import partial
import importlib
import types

from aosxtools.utils.probe import probe
from aosxtools.proxyagents.nxos.connector import NxosConnector as Connector
from aosxtools.proxyagents.nxos import exceptions as NxosExc


__all__ = ['NxosDevice']


class NxosDevice(object):
    DEFAULT_PROBE_TIMEOUT = 3

    def __init__(self, target, **kwargs):
        self.target = target

        user = kwargs.get('user', 'admin')
        passwd = kwargs.get('passwd', 'admin')

        self.api = Connector(hostname=self.target, user=user, passwd=passwd)

        self.facts = {}

        if not 'no_probe' in kwargs:
            self.probe(**kwargs)

        if not 'no_gather_facts' in kwargs:
            self.gather_facts()


    def probe(self, **kwargs):
        timeout = kwargs.get('timeout') or self.DEFAULT_PROBE_TIMEOUT
        ok, elapsed = probe(self.target, protocol=self.api.proto, timeout=timeout)
        if not ok:
            raise NxosExc.ProbeError()

    def close(self):
        # nothing to do for close at this time, yo!
        pass

    def gather_facts(self):
        exec_show = partial(self.api.exec_opcmd, resp_fmt='json')

        facts = self.facts

        facts['vendor'] = 'cisco'
        facts['os'] = 'nxos'

        got = exec_show('show hostname')
        facts['fqdn'] = got['hostname']
        facts['hostname'], _, facts['domain_name'] = facts['fqdn'].partition('.')

        got = exec_show('show hardware')
        facts['version'] = got['kickstart_ver_str']
        facts['chassis_id'] = got['chassis_id']
        facts['virtual'] = bool('NX-OSv' in facts['chassis_id'])

        row = got['TABLE_slot']['ROW_slot']['TABLE_slot_info']['ROW_slot_info'][0]
        facts['model'] = row['model_num']
        facts['serial_number'] = row['serial_num']
        facts['part_number'] = row['part_num']
        facts['part_version'] = row['part_revision']
        facts['hw_version'] = row['hw_ver']

    def __getattr__(self, item):
        ###
        ### this is rather perhaps being a bit "too clever", but I sometimes
        ### can't help myself ;-P
        ###

        # if the named addon module does not exist, this will raise
        # an ImportError.  We might want to catch this and handle differently

        mod = importlib.import_module('.addons.%s' % item, package=__package__)

        def wrapper(*vargs, **kvargs):
            cls = getattr(mod, item.capitalize())
            self.__dict__[item] = cls(self, *vargs, **kvargs)

        return wrapper



