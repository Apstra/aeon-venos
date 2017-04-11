from mock import patch, Mock
import pytest

from aeon.exceptions import ProbeError
from aeon.base.device import BaseDevice


@patch('pylib.aeon.base.device.socket.socket')
def test_base_device_probeerror(mock_socket):
    mock_socket.return_value.connect.side_effect = Exception()
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    mock_con = Mock(proto='ssh')
    mock_con.return_value.proto = 'ssh'
    with pytest.raises(ProbeError):
        BaseDevice(target, connector=mock_con, user=user, passwd=passwd)


@patch('pylib.aeon.base.device.socket.socket')
def test_base_device(mock_socket):
    target = '1.1.1.1'
    user = 'test_user'
    passwd = 'test_passwd'
    mock_con = Mock(proto='ssh')
    mock_con.return_value.proto = 'ssh'
    bd = BaseDevice(target, connector=mock_con, user=user, passwd=passwd)
