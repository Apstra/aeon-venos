# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import os
import argparse
import logging

import aeon.exceptions as exceptions


class ArgumentParser(argparse.ArgumentParser):
    class ParserError(Exception):
        pass

    def error(self, message):
        raise ArgumentParser.ParserError(message)


class Stdargs(object):
    _ENV = {
        'TARGET_USER': 'AEON_TUSER',
        'TARGET_PASSWD': 'AEON_TPASSWD',
        'TARGET': 'AEON_TARGET',
        'LOGFILE': 'AEON_LOGFILE'
    }

    def __init__(self, **kwargs):
        self.progname = kwargs.get('name', 'aeon-nxos')
        self.psr = ArgumentParser(**kwargs)

        self.args = None
        self.target = None
        self.user = None
        self.passwd = None
        self.log = None

        self._setup_stdargs()

    def _setup_stdargs(self):
        self.psr.add_argument(
            '-t', '--target',
            default=os.getenv(Stdargs._ENV['TARGET']),
            help='Target hostname or ip-addr')

        self.psr.add_argument(
            '--logfile',
            default=os.getenv(Stdargs._ENV['LOGFILE']),
            help='name of log file')

        self.psr.add_argument(
            '--json',
            action='store_true', default=True,
            help='output in JSON')

        group = self.psr.add_argument_group('authentication')

        group.add_argument(
            '-u', '--user',
            help='Target username')

        group.add_argument(
            '-U', dest='env_user',
            default=Stdargs._ENV['TARGET_USER'],
            help='Target username environment variable')

        group.add_argument(
            '-P', dest='env_passwd',
            default=Stdargs._ENV['TARGET_PASSWD'],
            help='Target password environment variable')

    def parse_args(self):
        self.args = self.psr.parse_args()

        self.target = self.args.target
        self.user = self.args.user or os.getenv(self.args.env_user)
        self.passwd = os.getenv(self.args.env_passwd)

        if not self.target:
            raise exceptions.TargetError('missing target value')
        if not self.user:
            raise exceptions.TargetError('missing username value')
        if not self.passwd:
            raise exceptions.TargetError('missing password value')

        self.log = logging.getLogger(name=self.progname)
        if self.args.logfile:
            self._setup_logging()

        return self.args

    def _setup_logging(self, level=logging.INFO):
        self.log.setLevel(level)
        fh = logging.FileHandler(self.args.logfile)

        fmt = logging.Formatter(
            '%(asctime)s:%(levelname)s: {target}:%(message)s'
            .format(target=self.args.target))

        fh.setFormatter(fmt)
        self.log.addHandler(fh)
