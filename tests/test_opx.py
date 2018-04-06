import mock
import pytest
from pylib.aeon.opx import device
from pylib.aeon.cumulus import connector


g_facts = {
    'hw_version': None,
    'hw_part_number': None,
    'hostname': 'opx221_vm',
    'serial_number': '525400A5EC36',
    'fqdn': 'opx221_vm',
    'os_version': '2.2.1',
    'virtual': True,
    'hw_model': 'S6000-VM',
    'vendor': 'OPX',
    'mac_address': '52:54:00:A5:EC:36',
    'os_name': 'OPX',
    'service_tag': None
}

ip_link_show_out = '''
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN mode DEFAULT group default
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:a5:ec:36 brd ff:ff:ff:ff:ff:ff
'''

hostname_out = "opx221_vm"
grep_version_out = '2.2.1'
grep_platform_out = 'S6000-VM'


@mock.patch('pylib.aeon.opx.connector.paramiko.SSHClient')
@pytest.fixture()
def opx_connector(mock_ssh):
    hostname = '1.1.1.1'
    port = 22
    proto = 'ssh'
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, proto=proto, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.opx.device.BaseDevice.probe')
@mock.patch('pylib.aeon.opx.device.Connector')
@pytest.fixture()
def opx_device(mock_connector, mock_probe, request):
    def mock_execute(args, **kwargs):
        results = []
        for arg in args:
            # os_version
            if arg == """grep -oP '^OS_VERSION=[\"]?\K.*\d' /etc/OPX-release-version""":
                results.append({'stdout': grep_version_out})
            # platform
            if arg == """grep -oP '^PLATFORM=[\"]?\K.*\w' /etc/OPX-release-version""":
                results.append({'stdout': grep_platform_out})
            # hostname
            elif arg == 'hostname':
                results.append({'stdout': hostname_out})
            elif arg =='ip link show':
                results.append({'stdout': ip_link_show_out})
        return True, results
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    return dev


def test_opx_device(opx_device):
    dev = opx_device
    assert dev.OS_NAME == 'OPX'
    assert dev.DEFAULT_PROBE_TIMEOUT == 10
    assert dev.user == 'test_user'
    assert dev.passwd == 'test_passwd'
    assert dev.facts == g_facts



