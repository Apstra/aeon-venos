# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import pyeapi
import socket
from copy import deepcopy

from aeon.exceptions import ConfigError, CommandError


__all__ = ['Connector']


class Connector(object):
    DEFAULT_PROTOCOL = 'http'
    VRF_MGMT = 'management'
    DEFAULT_VRF = 'default'

    def __init__(self, hostname, **kwargs):
        self.vrf = self.VRF_MGMT

        self.hostname = hostname
        self.proto = kwargs.get('proto') or self.DEFAULT_PROTOCOL
        self.port = kwargs.get('port')

        # explicit check for None, since setting port to 0 is
        # valid for on-box EOS.

        if self.port is None:
            self.port = socket.getservbyname(self.proto)

        self.user = kwargs.get('user')
        self.passwd = kwargs.get('passwd')

        if self.proto == 'socket':
            self.eapi = pyeapi.client.make_connection(
                'socket', username=self.user, password=self.passwd,
                **kwargs.get('socket_opts'))
        else:
            self.eapi = pyeapi.connect(
                transport=self.proto, host=self.hostname,
                username=self.user, password=self.passwd)

    def execute(self, commands, encoding='json'):

        # Make a copy of commands so that commands object isn't mutated outside of this function
        commands = deepcopy(commands)

        # Convert to list if not already a list
        commands = commands if isinstance(commands, list) else [commands]

        # Add 'enable' if not the first enty in the commands list
        if commands[0] != 'enable':
            commands.insert(0, 'enable')
        try:
            got = self.eapi.execute(commands=commands, encoding=encoding)
        except Exception as exc:
            raise CommandError(exc=exc, commands=commands)

        # get the results.  if ther was only one command return the actual
        # results item (vs. making the caller do [0]).

        results = got['result']
        results.pop(0)
        return results if len(results) > 1 else results.pop()

    def configure(self, contents):
        if not isinstance(contents, list):
            raise RuntimeError('contents must be a list, for now')

        contents = ['enable', 'configure'] + filter(bool, contents)   # filters out empty lines

        try:
            self.eapi.execute(contents)
        except Exception as exc:
            raise ConfigError(exc=exc, contents=contents)
