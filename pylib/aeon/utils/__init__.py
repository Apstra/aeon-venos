# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import socket

import paramiko
import pexpect
from pexpect import pxssh

import aeon.nxos.device
import aeon.eos.device
import aeon.cumulus.device
import aeon.ubuntu.device
import aeon.centos.device
from aeon.exceptions import TargetError


def get_device(target=None, user='admin', passwd='admin', nos_only=False):
    """
    Automatically determine device type based on device interrogation.
    :param target: IP address or hostname of target
    :param user: Username to login to target
    :param passwd: Password to login to target
    :param nos_only: Only check for device nos and return as string, do not return device object
    :return: Device object
    """
    dev_table = {
        'nxos': aeon.nxos.device.Device,
        'eos': aeon.eos.device.Device,
        'cumulus': aeon.cumulus.device.Device,
        'ubuntu': aeon.ubuntu.device.Device,
        'centos': aeon.centos.device.Device
    }
    try:
        # Use paramiko to check if device is reachable because pxssh is bad at that.
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(target, username=user, password=passwd, timeout=5)
        ssh.close()
    except socket.error:
        raise TargetError('Device unreachable: %s' % target)
    except paramiko.AuthenticationException:
        raise TargetError('Authentication error: %s' % target)
    except paramiko.SSHException:
        raise TargetError('Error logging in: %s' % target)

    try:
        nos = ''
        session = pxssh.pxssh(timeout=10, options={'StrictHostKeyChecking': "no",
                                       'UserKnownHostsFile': "/dev/null"})
        session.force_password = True
        session.PROMPT = '\r\n.*#|\r\n.*$'
        session.login(target, user, password=passwd, auto_prompt_reset=False, login_timeout=10)
        session.sendline('show version')
        i = session.expect(['Cisco', 'Arista', 'command not found', 'not installed', pexpect.TIMEOUT], timeout=10)
        if i == 0:
            nos = 'nxos'
        if i == 1:
            nos = 'eos'

        if i == 2 or i == 3:
            session.sendline('cat /proc/version')
            i = session.expect(['cumulus', 'Ubuntu', 'Red Hat', pexpect.TIMEOUT], timeout=5)
            if i == 0:
                nos = 'cumulus'
            if i == 1:
                nos = 'ubuntu'
            if i == 2:
                nos = 'centos'
            if i == 3:
                session.sendline('[ -f /etc/opx/opx-environment.sh ] && echo "device is OPX" || echo "Not found"')
                i = session.expect(['Not found', 'device is OPX', pexpect.TIMEOUT], timeout=5)
                if i == 0 or i == 2:
                    raise TargetError('Unable to determine device type for %s' % target)
                if i == 1:
                    nos = 'opx'
        if i == 4:
            raise TargetError('Unable to determine device type for %s' % target)

    except pxssh.ExceptionPxssh as e:
        raise TargetError("Error logging in to {target} : {error}".format(target=target, error=e))

    finally:
        session.close()

    if nos_only:
        return nos
    else:
        return dev_table[nos](target, user=user, passwd=passwd)
