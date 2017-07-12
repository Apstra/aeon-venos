import mock
import pytest
from pylib.aeon.centos import device
from pylib.aeon.cumulus import connector


g_facts = {
    'hw_version': None,
    'hw_part_number': None,
    'hostname': 'centos',
    'serial_number': None,
    'fqdn': 'centos',
    'os_version': 'CentOS 6.8',
    'virtual': None,
    'hw_model': 'Server',
    'vendor': 'CentOS',
    'mac_address': '01:23:45:67:89:0A',
    'os_name': 'centos',
    'service_tag': None
}

ip_link_show_dev_eth0_out = '''
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master mgmt state UP mode DEFAULT group default qlen 1000
    link/ether 01:23:45:67:89:0a brd ff:ff:ff:ff:ff:ff
'''

hostname_out = "centos"
cat_version_out = "CentOS 6.8"


@mock.patch('pylib.aeon.centos.connector.paramiko.SSHClient')
@pytest.fixture()
def centos_connector(mock_ssh):
    hostname = '1.1.1.1'
    port = 22
    proto = 'ssh'
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, proto=proto, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.centos.device.BaseDevice.probe')
@mock.patch('pylib.aeon.centos.device.Connector')
@pytest.fixture()
def centos_device(mock_connector, mock_probe, request):
    def mock_execute(args, **kwargs):
        results = []
        for arg in args:
            # os_version
            if arg == 'cat /etc/centos-release | cut -d" " -f3':
                results.append({'stdout': cat_version_out})
            # hostname
            elif arg == 'hostname':
                results.append({'stdout': hostname_out})
            elif arg =='/sbin/ip link show dev eth0':
                results.append({'stdout': ip_link_show_dev_eth0_out})
        return True, results
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    return dev


def test_centos_device(centos_device):
    dev = centos_device
    assert dev.OS_NAME == 'centos'
    assert dev.DEFAULT_PROBE_TIMEOUT == 10
    assert dev.user == 'test_user'
    assert dev.passwd == 'test_passwd'
    assert dev.facts == g_facts



