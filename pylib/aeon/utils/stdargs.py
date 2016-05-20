import os
import argparse


class ArgumentParser(argparse.ArgumentParser):
    class ParserError(Exception):
        pass

    def error(self, message):
        raise ArgumentParser.ParserError(message)


class Stdargs(object):
    def __init__(self, name, description=None):
        self.psr = ArgumentParser(
            prog=name,
            description=description or name,
            add_help=True)

        self.target = None
        self.user = None
        self.passwd = None

        self._setup_stdargs()

    def _setup_stdargs(self):
        self.psr.add_argument(
            '-t', '--target',
            help='hostname or ip_addr of target device',
            required=True)

        self.psr.add_argument(
            '-u', '--user',
            help='login user-name')

        self.psr.add_argument(
            '-U', '--env-user',
            help='env variable containing username')

        self.psr.add_argument(
            '-P', '--env-passwd',
            help='env variable containing passwd')

        self.psr.add_argument(
            '--json',
            action='store_true', default=True,
            help='output in JSON')

    def parse_args(self):
        self.args = self.psr.parse_args()

        self.target = self.args.target
        self.user = self.args.user or os.getenv(self.args.env_user)
        self.passwd = os.getenv(self.args.env_passwd)

        return self.args
