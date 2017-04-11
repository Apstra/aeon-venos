import mock
import pytest
from pylib.aeon.cumulus import connector, device
from aeon.exceptions import LoginNotReadyError, ProbeError


g_facts = {
    'hw_version': '1',
    'hw_part_number': '123ABC',
    'hostname': 'cumulussw',
    'serial_number': '0123456789ABCDEF1011',
    'fqdn': 'cumulussw',
    'os_version': '1.0.0',
    'virtual': False,
    'hw_model': 'Cumulus1000',
    'vendor': 'Cumulus',
    'mac_address': '01:23:45:67:89:0a',
    'os_name': 'cumulus',
    'service_tag': 'no-service-tag'
}

virt2_facts = {
    'hw_part_number': None,
    'virtual': True,
    'hw_model': 'CUMULUS-VX',
    'vendor': 'CUMULUS-NETWORKS',
    'service_tag': None,
    'hw_version': None,
    'serial_number': g_facts['mac_address'].upper(),
    'mac_address': g_facts['mac_address'].upper()
}

# Cumulus 2.x Virtual device
g_facts_virt2 = dict(g_facts)
g_facts_virt2.update(virt2_facts)

decode_syseeprom = '''
TLV Name             Code Len Value
-------------------- ---- --- -----
Product Name         0x21   8 Cumulus1000
Part Number          0x22   6 123ABC
Serial Number        0x23  20 0123456789ABCDEF1011
Base MAC Address     0x24   6 01:23:45:67:89:0a
Vendor Name          0x2D   4 Cumulus
Label Revision       0x08   1 1
'''

ip_link_show_dev_eth0 = '''
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast master mgmt state UP mode DEFAULT group default qlen 1000
    link/ether 01:23:45:67:89:0a brd ff:ff:ff:ff:ff:ff
'''

@mock.patch('pylib.aeon.cumulus.connector.paramiko.SSHClient')
@pytest.fixture()
def cumulus_connector(mock_ssh):
    hostname = '1.1.1.1'
    port = 22
    proto = 'ssh'
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, proto=proto, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.cumulus.device.BaseDevice.probe')
@mock.patch('pylib.aeon.cumulus.device.Connector')
@pytest.fixture(params=[g_facts, g_facts_virt2], ids=['physical', 'virtual'])
def cumulus_device(mock_connector, mock_probe, request):
    def mock_execute(args, **kwargs):
        results = []
        for arg in args:
            # os_version
            if arg == 'cat /etc/lsb-release | grep RELEASE | cut -d= -f2':
                results.append({'stdout': request.param['os_version']})
            # hostname
            elif arg == 'hostname':
                results.append({'stdout': request.param['hostname']})
            # test if dev is virtual Cumulus OS 2.x (return sets device to not be virt2
            elif arg == 'test -e /usr/cumulus/bin/decode-syseeprom':
                if request.param['virtual']:
                    results.append({'exit_code': 1})
                else:
                    results.append({'exit_code': 0})
            elif arg =='sudo decode-syseeprom':
                results.append({'stdout':decode_syseeprom})
            elif arg =='ip link show dev eth0':
                results.append({'stdout': ip_link_show_dev_eth0})
        return True, results
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    return dev


def test_cumulus_connector(cumulus_connector):
    con = cumulus_connector
    assert con.hostname == '1.1.1.1'
    assert con.port == 22
    assert con.user == 'test_user'
    assert con.passwd == 'test_passwd'
    con.close()


@mock.patch('pylib.aeon.cumulus.connector.paramiko.SSHClient')
def test_cumulus_connector_exception(mock_ssh):
    mock_ssh.return_value.connect.side_effect = Exception
    hostname = '1.1.1.1'
    port = 22
    user = 'test_user'
    passwd = 'test_passwd'
    with pytest.raises(LoginNotReadyError):
        con = connector.Connector(hostname, port=port, user=user, passwd=passwd)


@mock.patch('pylib.aeon.cumulus.connector.paramiko.SSHClient')
def test_cumulus_connector_execute(mock_ssh):
    mock_stdin = mock.MagicMock()
    mock_stdout = mock.MagicMock()
    mock_stderr = mock.MagicMock()
    mock_stdout.read.return_value = 'stdout text'
    mock_stderr.read.return_value = 'stderr text'
    # Set exit status to 0 for test1 and test2 in results_good, but 1 for results_bad
    mock_stdout.channel.recv_exit_status.side_effect = [0, 0, 1, 1, 1]
    mock_ssh.return_value.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    results_good = con.execute(['test1', 'test2'])
    assert results_good == (True, [{'cmd': 'test1',
                              'exit_code': 0,
                              'stderr': 'stderr text',
                              'stdout': 'stdout text'
                               },
                              {'cmd': 'test2',
                               'exit_code': 0,
                               'stderr': 'stderr text',
                               'stdout': 'stdout text'
                               }])
    results_bad = con.execute(['test1', 'test2'])
    assert results_bad == (False, [{'cmd': 'test1',
                              'exit_code': 1,
                              'stderr': 'stderr text',
                              'stdout': 'stdout text'
                               }])
    results_bad_no_stop = con.execute(['test1', 'test2'], stop_on_error=False)
    assert results_bad_no_stop == (False, [{'cmd': 'test1',
                              'exit_code': 1,
                              'stderr': 'stderr text',
                              'stdout': 'stdout text'
                               },
                              {'cmd': 'test2',
                               'exit_code': 1,
                               'stderr': 'stderr text',
                               'stdout': 'stdout text'
                               }])


def test_cumulus_device(cumulus_device):
    dev = cumulus_device
    assert dev.OS_NAME == 'cumulus'
    assert dev.DEFAULT_PROBE_TIMEOUT == 3
    assert dev.user == 'test_user'
    assert dev.passwd == 'test_passwd'
    if dev.facts['virtual']:
        assert dev.facts == g_facts_virt2
    else:
        assert dev.facts == g_facts



