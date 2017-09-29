# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import pexpect
from pexpect import pxssh

import aeon.nxos.device
import aeon.eos.device
import aeon.cumulus.device
import aeon.ubuntu.device
import aeon.centos.device
from aeon.exceptions import TargetError


def get_device(target=None, user='admin', passwd='admin'):
    """
    Automatically determine device type based on device interrogation.
    :param target: IP address or hostname of target
    :param user: Username to login to target
    :param passwd: Password to login to target
    :return: Device object
    """
    try:
        session = pxssh.pxssh(timeout=10, options={'StrictHostKeyChecking': "no",
                                       'UserKnownHostsFile': "/dev/null"})
        session.force_password = True
        session.PROMPT = '\r\n.*#|\r\n.*$'
        session.login(target, user, password=passwd, auto_prompt_reset=False, login_timeout=10)

        session.sendline('show version')
        i = session.expect(['Cisco', 'Arista', 'command not found', 'not installed', pexpect.TIMEOUT], timeout=10)
        if i == 0:
            return aeon.nxos.device.Device(target, user=user, passwd=passwd)
        if i == 1:
            return aeon.eos.device.Device(target, user=user, passwd=passwd)
        if i == 2 or i == 3:
            pass

        session.sendline('cat /proc/version')
        i = session.expect(['cumulus', 'Ubuntu', 'Red Hat'], timeout=10)
        if i == 0:
            return aeon.cumulus.device.Device(target, user=user, passwd=passwd)
        if i == 1:
            return aeon.ubuntu.device.Device(target, user=user, passwd=passwd)
        if i == 2:
            return aeon.centos.device.Device(target, user=user, passwd=passwd)
        if i == 3:
            raise TargetError('Unable to determine device type for %s' % target)

    except pxssh.ExceptionPxssh as e:
        return "Error logging in: %s" % e

    finally:
        session.close()
