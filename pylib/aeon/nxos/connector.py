# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import re
from lxml import etree
import requests
from requests.auth import HTTPBasicAuth
from copy import copy

import socket

from aeon import exceptions
from aeon.nxos import exceptions as NxosExc


_RE_CONF = re.compile(r"\n\n?\s*")

__all__ = ['NxosConnector']

_NXOS_RESP_XPATH_BODY = 'outputs/output/body'
_NXOS_RESP_XPATH_HTTPCODE = 'outputs/output/code'
_NXOS_RESP_XPATH_CLIERR = 'outputs/output/clierror'


class NxosRequest(object):
    MESSGE_TYPES = ('cli_show', 'cli_show_ascii', 'cli_conf')
    OUTPUT_FMTS = ('json', 'xml')
    CHUNK_VALUES = (0, 1)

    # !! WARNING !! the following string must not contain a leading newline ...
    # !! WARNING !! that is, it must start immediately following the triple-quote

    MESSAGE = """<?xml version="1.0"?>
<ins_api>
<type>{msg_type}</type>
<version>{api_ver}</version>
<chunk>{chunk}</chunk>
<sid>{session_id}</sid>
<input>{command}</input>
<output_format>{resp_fmt}</output_format>
</ins_api>
"""

    DEFAULTS = dict(
        msg_type='cli_show',
        api_ver='0.1',
        chunk=0,
        session_id=1,
        resp_fmt='json',
        command=None
    )

    def __init__(self):
        self.__dict__['params'] = copy(self.DEFAULTS)

    def send(self, api, timeout=None):
        _timeout = timeout if timeout is not None else api.DEFAULT_TIMEOUT
        try:
            resp = requests.post(
                api.api_url, headers=api.api_headers,
                timeout=_timeout,
                auth=api.api_auth, data=str(self))

        except requests.exceptions.ReadTimeout as exc:
            cmd_exc = exceptions.TimeoutError(exc)
            cmd_exc.timeout = timeout
            raise cmd_exc

        except Exception as exc:
            raise NxosExc.RequestError(exc)

        if 401 == resp.status_code:
            cmd_exc = exceptions.UnauthorizedError()
            cmd_exc.message = 'not authorized'
            raise cmd_exc

        if 200 != resp.status_code:
            cmd_exc = NxosExc.CommandError()
            cmd_exc.errorcode = resp.status_code
            cmd_exc.message = "command failed, http_code={0} http_reason={1}".format(
                resp.status_code, resp.reason)
            raise cmd_exc

        return resp

    def __setattr__(self, key, value):
        if key in self.__dict__['params'] and value is not None:
            self.__dict__['params'][key] = value

    def __getattr__(self, item):
        return self.__dict__.get(item) or self.__dict__.get('params').get(item)

    def __str__(self):
        return self.MESSAGE.format(**self.params)


class NxosOperRequest(NxosRequest):
    def __init__(self, command=None):
        super(self.__class__, self).__init__()
        self.command = command


class NxosConfigRequest(NxosRequest):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.msg_type = 'cli_conf'
        self.resp_fmt = 'xml'


class NxosConnector(object):
    DEFAULT_PROTOCOL = 'http'
    DEFAULT_TIMEOUT = 60

    def __init__(self, hostname, **kwargs):
        self.hostname = hostname

        self.proto = kwargs.get('proto') or self.DEFAULT_PROTOCOL
        self.port = kwargs.get('port') or socket.getservbyname(self.proto)

        self.api_url = "{proto}://{target}:{port}/ins".format(
            proto=self.proto, port=self.port, target=self.hostname)

        self.api_headers = {
            'cookie': 'no-cookie',
            'content-type': 'text/xml'
        }

        self.user = kwargs.get('user')
        self.passwd = kwargs.get('passwd')

    # ---------------------------------------------------------------
    #                             PROPERTIES
    # ---------------------------------------------------------------

    @property
    def passwd(self):
        """ passwd is write-only """
        raise RuntimeError("passwd property is write-only")

    @passwd.setter
    def passwd(self, value):
        """ changes the auth user-password """
        self._passwd = value

    @property
    def api_auth(self):
        return HTTPBasicAuth(self.user, self._passwd)

    def exec_config(self, contents, timeout=None):
        rqst = NxosConfigRequest()
        rqst.command = _RE_CONF.sub(' ; ', contents)

        resp = rqst.send(self, timeout)

        # now we need to check the contents of the NX-API response ...
        # we will just check for one instance right now ... may try to gather
        # all of them &| include the XML body as part of the exception at some
        # later point in time.

        as_xml = etree.XML(resp.text)
        cli_error = as_xml.find(_NXOS_RESP_XPATH_CLIERR)
        if cli_error is not None:
            raise NxosExc.CommandError(cli_error.text)

        # config OK, yea!
        return True

    def exec_opcmd(self, command, raw_resp=False, timeout=None, **kwargs):

        rqst = NxosOperRequest(command=command)
        rqst.msg_type = kwargs.get('msg_type')
        rqst.resp_fmt = kwargs.get('resp_fmt')

        resp = rqst.send(self, timeout)

        def rsp_is_xml():
            as_xml = etree.XML(resp.text)
            if raw_resp is True:
                return as_xml

            return as_xml.find(_NXOS_RESP_XPATH_BODY)

        def rsp_is_json():
            as_json = resp.json()
            outputs = as_json['ins_api']['outputs']['output']

            if 'clierror' in outputs:
                raise NxosExc.CommandError(outputs['clierror'])

            return as_json if raw_resp is True else outputs['body']

        proc_rsp = rsp_is_json if 'json' == rqst.resp_fmt else rsp_is_xml
        return proc_rsp()
