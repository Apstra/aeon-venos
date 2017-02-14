import mock
import pytest
from pylib.aeon.cumulus import connector, device


@mock.patch('pylib.aeon.cumulus.connector.paramiko.SSHClient')
@pytest.fixture()
def cumulus_connector(mock_ssh):
    hostname = '1.1.1.1'
    port = 22
    user = 'test_user'
    passwd = 'test_passwd'
    con = connector.Connector(hostname, port=port, user=user, passwd=passwd)
    return con


@mock.patch('pylib.aeon.cumulus.connector.paramiko.SSHClient')
@pytest.fixture
def cumulus_device(mock_ssh):
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    dev = device.Device(target, user=user, passwd=passwd, no_probe=True, no_gather_facts=True)
    return dev


def test_cumulus_connector(cumulus_connector):
    con = cumulus_connector
    assert con.hostname == '1.1.1.1'
    assert con.port == 22
    assert con.user == 'test_user'
    assert con.passwd == 'test_passwd'


def test_cumulus_device(cumulus_device):
    #mock_probe.return_value = (True, 1)
    dev = cumulus_device
    assert dev.OS_NAME == 'cumulus'
    assert dev.DEFAULT_PROBE_TIMEOUT == 3
    assert dev.DEFAULT_USER == 'admin'
    assert dev.DEFAULT_PASSWD == 'admin'