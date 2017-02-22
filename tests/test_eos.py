import mock
import pytest
from pylib.aeon.eos import connector, device, exceptions
from aeon.exceptions import ProbeError, CommandError, ConfigError


g_facts = {'hw_version': '1.0.1',
           'hw_part_number': None,
           'hostname': 'aristasw',
           'serial_number': '0123456789',
           'chassis_id': None,
           'fqdn': 'aristasw.device.com',
           'os_version': '1.0.0',
           'virtual': False,
           'hw_model': 'Arista1000',
           'vendor': 'arista',
           'hw_part_version': None,
           'os': 'eos'
           }

show_ver_return = {'version': g_facts['os_version'],
    'modelName': g_facts['hw_model'],
    'hardwareRevision': g_facts['hw_version'],
    'systemMacAddress': '00:11:22:33:44:55:66:77',
    'serialNumber': g_facts['serial_number']}

show_hostname_return = {
    'fqdn': 'aristasw.device.com',
    'hostname': 'aristasw'
}


@mock.patch('pylib.aeon.eos.connector.pyeapi')
@pytest.fixture()
def eos_connector(mock_eapi):
    hostname = '1.1.1.1'
    port = 22
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.eos.device.probe')
@mock.patch('pylib.aeon.eos.device.Connector')
@pytest.fixture
def eos_device(mock_connector, mock_probe):
    def mock_execute(*args, **kwargs):
        if args[0] == 'show version':
            return show_ver_return
        elif args[0] == 'show hostname':
            return show_hostname_return
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    return dev


def test_eos_connector(eos_connector):
    con = eos_connector
    assert con.hostname == '1.1.1.1'
    assert con.port == 22
    assert con.user == 'test_user'
    assert con.passwd == 'test_passwd'


def test_eos_device(eos_device):
    dev = eos_device
    assert dev.DEFAULT_PROBE_TIMEOUT == 3
    assert dev.DEFAULT_USER == 'admin'
    assert dev.DEFAULT_PASSWD == 'admin'
    assert dev.facts == g_facts


@mock.patch('pylib.aeon.eos.device.probe')
@mock.patch('pylib.aeon.eos.device.Connector')
def test_eos_device_probe_error(mock_connector, mock_probe):
    def mock_execute(*args, **kwargs):
        if args[0] == 'show version':
            return show_ver_return
        elif args[0] == 'show hostname':
            return show_hostname_return
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = False, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    with pytest.raises(ProbeError) as e:
        dev = device.Device(target, user=user, passwd=passwd)


@mock.patch('pylib.aeon.eos.device.probe')
@mock.patch('pylib.aeon.eos.device.Connector')
def test_eos_device_no_fqdn_no_hostname(mock_connector, mock_probe):
    def mock_execute(*args, **kwargs):
        if args[0] == 'show version':
            return show_ver_return
        elif args[0] == 'show hostname':
            raise Exception
    mock_connector.return_value.execute.side_effect = mock_execute
    mock_probe.return_value = True, 10
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd)
    assert dev.facts['fqdn'] == dev.facts['hostname'] == 'localhost'


def test_eos_exception():
    with pytest.raises(exceptions.EosException):
        raise exceptions.EosException


# def test_eos_connector_execute():
#
#     #mock_pyeapi.return_value.execute.return_value = {'result': 'good stuff'}
#     con = eos_connector
#     with mock.patch('pylib.aeon.eos.device.Connector.eapi') as mock_eapi:
#         mock_eapi.return_value = Exception
#         with pytest.raises(Exception):
#
#             print con
#             results = con.execute('test')
#             print results


@mock.patch('pylib.aeon.eos.connector.pyeapi.connect')
def test_eos_connector_execute_exception(mock_eapi):
    mock_eapi.return_value.execute.side_effect = Exception
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    with pytest.raises(CommandError):
        con.execute('test')


@mock.patch('pylib.aeon.eos.connector.pyeapi.connect')
def test_eos_connector_execute(mock_eapi):
    def mock_execute(*args):
        return {'result': list(args)[0]}

    mock_eapi.return_value.execute.side_effect = mock_execute
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    results = con.execute(['test1', 'test2'])
    assert results == ['test1', 'test2']


@mock.patch('pylib.aeon.eos.connector.pyeapi.connect')
def test_eos_connector_configure_exception(mock_eapi):
    mock_eapi.return_value.execute.side_effect = Exception
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    with pytest.raises(ConfigError):
        con.configure(['test'])


@mock.patch('pylib.aeon.eos.connector.pyeapi.connect')
def test_eos_connector_configure_runtime_exception(mock_eapi):
    mock_eapi.return_value.execute.side_effect = Exception
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    with pytest.raises(RuntimeError) as e:
        con.configure('test')


@mock.patch('pylib.aeon.eos.connector.pyeapi.connect')
def test_eos_connector_configure(mock_eapi):
    def mock_execute(*args):
        return {'result': list(args)[0]}

    mock_eapi.return_value.execute.side_effect = mock_execute
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'

    con = connector.Connector(target, user=user, passwd=passwd)
    con.configure(['test1', 'test2', ''])
    expected = [mock.call(host=target, password=passwd, transport='http', username=user),
                mock.call().execute(['enable', 'configure', 'test1', 'test2'])]
    assert mock_eapi.mock_calls == expected
