from mock import patch, Mock, call
import pytest
from pexpect.pxssh import ExceptionPxssh
from aeon.exceptions import TargetError

from aeon.utils import get_device

dev_info = {'target': '1.1.1.1',
       'user': 'test_user',
       'passwd': 'test_passwd'}
nos_only_params = [True, False]


@patch('pylib.aeon.utils.aeon.nxos.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_login(mock_pxssh, mock_nxos_device):
    mock_pxssh.return_value.expect.return_value = 0
    get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    mock_pxssh.return_value.login.assert_called_with(dev_info['target'],
                                                     dev_info['user'],
                                                     auto_prompt_reset=False,
                                                     login_timeout=10,
                                                     password=dev_info['passwd'])


@patch('pylib.aeon.utils.aeon.cumulus.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_sendline(mock_pxssh, mock_nxos_device):
    mock_pxssh.return_value.expect.side_effect = [2, 0]
    get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    calls = [call('show version'), call('cat /proc/version')]
    mock_pxssh.return_value.sendline.assert_has_calls(calls)


@patch('pylib.aeon.utils.aeon.nxos.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_nxos(mock_pxssh, mock_nxos_device):
    device_name = 'nxos_device'
    mock_pxssh.return_value.expect.return_value = 0
    mock_nxos_device.return_value = device_name
    dev = get_device(target=dev_info['target'],
                     user=dev_info['user'],
                     passwd=dev_info['passwd'])
    assert dev == device_name


@patch('pylib.aeon.utils.aeon.nxos.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_nos_only(mock_pxssh, mock_nxos_device):
    device_name = 'nxos'
    mock_pxssh.return_value.expect.return_value = 0
    mock_nxos_device.return_value = device_name
    dev = get_device(target=dev_info['target'],
                     user=dev_info['user'],
                     passwd=dev_info['passwd'],
                     nos_only=True)
    assert dev == device_name

@patch('pylib.aeon.utils.aeon.eos.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_eos(mock_pxssh, mock_eos_device):
    device_name = 'eos_device'
    mock_pxssh.return_value.expect.return_value = 1
    mock_eos_device.return_value = device_name
    dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    assert dev == device_name


@patch('pylib.aeon.utils.aeon.cumulus.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_cumulus(mock_pxssh, mock_cumulus_device):
    device_name = 'cumulus_device'
    mock_pxssh.return_value.expect.side_effect = [2, 0]
    mock_cumulus_device.return_value = device_name
    dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    assert dev == device_name


@patch('pylib.aeon.utils.aeon.ubuntu.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_ubuntu(mock_pxssh, mock_ubuntu_device):
    device_name = 'ubuntu_device'
    mock_pxssh.return_value.expect.side_effect = [2, 1]
    mock_ubuntu_device.return_value = device_name
    dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    assert dev == device_name


@patch('pylib.aeon.utils.aeon.centos.device.Device')
@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_centos(mock_pxssh, mock_centos_device):
    device_name = 'centos_device'
    mock_pxssh.return_value.expect.side_effect = [2, 2]
    mock_centos_device.return_value = device_name
    dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
    assert dev == device_name


@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_target_error(mock_pxssh):
    mock_pxssh.return_value.expect.side_effect = [2, 3]
    with pytest.raises(TargetError) as e:
        dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
        assert e.message('Unable to determine device type for %s' % dev_info['target'])


@patch('pylib.aeon.utils.pexpect.pxssh.pxssh')
def test_get_device_exception(mock_pxssh):
    exception_msg = 'Test Exception Message'
    mock_pxssh.return_value.login.side_effect = ExceptionPxssh(exception_msg)
    with pytest.raises(TargetError) as e:
        dev = get_device(target=dev_info['target'], user=dev_info['user'], passwd=dev_info['passwd'])
        assert e.message('Error logging in: %s' % dev_info['target'])
