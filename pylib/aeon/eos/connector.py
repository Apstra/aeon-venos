import pyeapi
import socket

__all__ = ['Connector']


class Connector(object):
    DEFAULT_PROTOCOL = 'http'

    def __init__(self, hostname, **kwargs):
        self.hostname = hostname
        self.proto = kwargs.get('proto') or self.DEFAULT_PROTOCOL
        self.port = kwargs.get('port') or socket.getservbyname(self.proto)
        self.user = kwargs.get('user')
        self.passwd = kwargs.get('passwd')

        self.eapi = pyeapi.connect(
            transport=self.proto, host=self.hostname,
            username=self.user, password=self.passwd)

    def execute(self, commands):
        return self.eapi.execute(commands)