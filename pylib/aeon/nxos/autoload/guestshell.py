# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from collections import namedtuple
import time
import logging
from functools import partial
from aeon.nxos.exceptions import CommandError

_MODEL_RC_LIMITS = {

}


class _guestshell(object):
    GUESTSHELL_CPU = 6
    GUESTSHELL_DISK = 1024
    GUESTSHELL_MEMORY = 3072

    Resources = namedtuple('Resources', 'cpu memory disk')

    def __init__(self, device,
                 cpu=GUESTSHELL_CPU, memory=GUESTSHELL_MEMORY,
                 disk=GUESTSHELL_DISK, log=None):

        self.device = device
        self.guestshell = partial(self.device.api.exec_opcmd, msg_type='cli_show_ascii')
        self.cli = self.device.api.exec_opcmd
        self.log = log or logging.getLogger()

        self.sz_max = {}
        self._get_sz_max()

        self.sz_need = _guestshell.Resources(
            cpu=min(cpu, self.sz_max['cpu']),
            memory=min(memory, self.sz_max['memory']),
            disk=min(disk, self.sz_max['disk']))

        self.sz_has = None
        self._state = None
        self.exists = False

    # ---------------------------------------------------------------
    # -----
    # -----                     PROPERTIES
    # -----
    # ---------------------------------------------------------------

    @property
    def state(self):
        cmd = 'show virtual-service detail name guestshell+'
        try:
            got = self.cli(cmd)
        except CommandError:
            # means there is no guestshell
            self.exists = False
            self._state = 'None'
            return self._state

        try:
            self._state = got['TABLE_detail']['ROW_detail']['state']
            return self._state
        except TypeError:
            # means there is no guestshell
            self.exists = False
            self._state = 'None'
            return self._state

    @property
    def size(self):
        self._get_sz_info()
        return self.sz_has

    # ---------------------------------------------------------------
    # -----
    # -----                     PUBLIC METHODS
    # -----
    # ---------------------------------------------------------------

    def setup(self):
        self.log.info("/START(guestshell): setup")

        state = self.state
        self.log.info("/INFO(guestshell): current state: %s" % state)

        if 'Activated' == state:
            self._get_sz_info()
            if self.sz_need != self.sz_has:
                self.log.info("/INFO(guestshell): need to resize, please wait...")
                self.resize()
                self.reboot()
        else:
            self.log.info(
                "/INFO(guestshell): not activated, enabling with proper size, "
                "please wait ...")
            self.resize()
            self.enable()

        self._get_sz_info()
        self.log.info("/END(guestshell): setup")

    def reboot(self):
        self.guestshell('guestshell reboot')
        self._wait_state('Activated')

    def enable(self):
        self.guestshell('guestshell enable')
        self._wait_state('Activated')

    def destroy(self):
        if 'None' == self.state:
            return

        if 'Activating' == self.state:
            self._wait_state('Activated')

        if 'Deactivating' == self.state:
            self._wait_state('Deactivated')

        self.guestshell('guestshell destroy')

        self._wait_state('None')

    def disable(self):
        self.guestshell('guestshell disable')
        self._wait_state('Deactivated')

    def resize_cpu(self, cpu):
        value = min(cpu, self.sz_max['cpu'])
        self.guestshell('guestshell resize cpu {}'.format(value))

    def resize_memory(self, memory):
        value = min(memory, self.sz_max['memory'])
        self.guestshell('guestshell resize memory {}'.format(value))

    def resize_disk(self, disk):
        value = min(disk, self.sz_max['disk'])
        self.guestshell('guestshell resize rootfs {}'.format(value))

    def resize(self):
        self.resize_cpu(self.sz_need.cpu)
        self.resize_memory(self.sz_need.memory)
        self.resize_disk(self.sz_need.disk)

    def run(self, command):
        return self.guestshell('guestshell run %s' % command)

    def sudoers(self, enable):
        """
        This method is used to enable/disable bash sudo commands running
        through the guestshell virtual service.  By default sudo access
        is prevented due to the setting in the 'sudoers' file.  Therefore
        the setting must be disabled in the file to enable sudo commands.

        This method assumes that the "bash-shell" feature is enabled.
        @@@ TO-DO: have a mech to check &| control bash-shell feature support

        :param enable:
            True - enables sudo commands
            False - disables sudo commands

        :return:
            returns the response of the sed command needed to make the
            file change
        """
        f_sudoers = "/isan/vdc_1/virtual-instance/guestshell+/rootfs/etc/sudoers"

        if enable is True:
            sed_cmd = r" 's/\(^Defaults *requiretty\)/#\1/g' "
        elif enable is False:
            sed_cmd = r" 's/^#\(Defaults *requiretty\)/\1/g' "
        else:
            raise RuntimeError('enable must be True or False')

        self.guestshell("run bash sudo sed -i" + sed_cmd + f_sudoers)

    # ---------------------------------------------------------------
    # -----
    # -----                     PRIVATE METHODS
    # -----
    # ---------------------------------------------------------------

    def _get_sz_max(self):
        got = self.cli('show virtual-service global')
        limits = got['TABLE_resource_limits']['ROW_resource_limits']
        for resource in limits:
            name = resource['media_name']
            max_val = int(resource['quota'])
            if 'CPU' in name:
                self.sz_max['cpu'] = max_val
            elif 'memory' in name:
                self.sz_max['memory'] = max_val
            elif 'flash' in name:
                self.sz_max['disk'] = max_val

    def _get_sz_info(self):
        """
        Obtains the current resource allocations, assumes that the
        guestshell is in an 'Activated' state
        """
        if 'None' == self._state:
            return None

        cmd = 'show virtual-service detail name guestshell+'
        got = self.cli(cmd)
        got = got['TABLE_detail']['ROW_detail']

        sz_cpu = int(got['cpu_reservation'])
        sz_disk = int(got['disk_reservation'])
        sz_memory = int(got['memory_reservation'])

        self.sz_has = _guestshell.Resources(
            cpu=sz_cpu, memory=sz_memory, disk=sz_disk)

    def _wait_state(self, state, timeout=60, interval=1, retry=0):
        now_state = None
        time.sleep(interval)

        while timeout:
            now_state = self.state
            if now_state == state:
                return
            time.sleep(interval)
            timeout -= 1

        if state == 'Activated' and now_state == 'Activating':
            # maybe give it some more time ...

            if retry > 2:
                msg = '/INFO(guestshell): waiting too long for Activated state'
                self.log.critical(msg)
                raise RuntimeError(msg)

            self.log.info('/INFO(guestshell): still Activating ... giving it some more time')
            self._wait_state(state, retry + 1)

        else:
            msg = '/INFO(guestshell): state %s never happened, still %s' % (state, now_state)
            self.log.critical(msg)
            raise RuntimeError(msg)
