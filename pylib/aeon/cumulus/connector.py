# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import socket
import paramiko
from aeon.exceptions import LoginNotReadyError


__all__ = ['Connector']


class Connector(object):
    DEFAULT_PROTOCOL = 'ssh'

    def __init__(self, hostname, **kwargs):
        self.hostname = hostname
        self.proto = kwargs.get('proto') or self.DEFAULT_PROTOCOL
        self.port = kwargs.get('port') or socket.getservbyname('ssh')
        self.user = kwargs.get('user')
        self.passwd = kwargs.get('passwd')

        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.open()

    def open(self):
        try:
            self._client.connect(
                self.hostname, port=self.port,
                username=self.user, password=self.passwd)

        except Exception as exc:
            raise LoginNotReadyError(exc=exc, message='Unable to connect.')

    def close(self):
        self._client.close()

    def execute(self, commands, stop_on_error=True):
        results = []
        exit_code_collector = 0

        for cmd in commands:
            stdin, stdout, stderr = self._client.exec_command(cmd)
            exit_code = stdout.channel.recv_exit_status()
            exit_code_collector |= exit_code

            results.append(dict(cmd=cmd, exit_code=exit_code,
                                stdout=stdout.read(),
                                stderr=stderr.read()))

            if stop_on_error is True and exit_code != 0:
                return False, results

        return bool(0 == exit_code_collector), results
