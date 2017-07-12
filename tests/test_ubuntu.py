import mock
import pytest
from pylib.aeon.ubuntu import device
from pylib.aeon.cumulus import connector


g_facts = {
    'hw_version': None,
    'hw_part_number': None,
    'hostname': 'ubuntu',
    'serial_number': None,
    'fqdn': 'ubuntu',
    'os_version': '14.04',
    'virtual': None,
    'hw_model': 'Server',
    'vendor': 'Canonical',
    'mac_address': '01:23:45:67:89:0A',
    'os_name': 'ubuntu',
    'service_tag': None
}

ip_link_show_dev_eth0_out = '''
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master mgmt state UP mode DEFAULT group default qlen 1000
    link/ether 01:23:45:67:89:0a brd ff:ff:ff:ff:ff:ff
'''

hostname_out = "ubuntu"
cat_version_out = "14.04"


@mock.patch('pylib.aeon.ubuntu.connector.paramiko.SSHClient')
@pytest.fixture()
def ubuntu_connector(mock_ssh):
    hostname = '1.1.1.1'
    port = 22
    proto = 'ssh'
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, proto=proto, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.ubuntu.device.BaseDevice.probe')
@mock.patch('pylib.aeon.ubuntu.device.Connector')
@pytest.fixture()
def ubuntu_device(mock_connector, mock_probe, request):
    def mock_execute(args, **kwargs):
        results = []
        for arg in args:
            # os_version
            if arg == 'cat /etc/lsb-release | grep RELEASE | cut -d= -f2':
                results.append({'stdout': cat_version_out})
            # hostname
            elif arg == 'hostname':
                results.append({'stdout': hostname_out})
            elif arg =='ip link show dev eth0':
                results.append({'stdout': ip_link_show_dev_eth0_out})
        return True, results
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    return dev


def test_ubuntu_device(ubuntu_device):
    dev = ubuntu_device
    assert dev.OS_NAME == 'ubuntu'
    assert dev.DEFAULT_PROBE_TIMEOUT == 10
    assert dev.user == 'test_user'
    assert dev.passwd == 'test_passwd'
    assert dev.facts == g_facts



