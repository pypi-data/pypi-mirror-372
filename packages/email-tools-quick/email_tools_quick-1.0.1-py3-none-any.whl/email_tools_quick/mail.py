# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import dataclasses
import socket
import ssl
import sys
import typing
from imaplib import IMAP4

import socks

IMAP4_PORT = 143
IMAP4_SSL_PORT = 993


def _default(value, default):
    if value is None:
        return default
    return value


@dataclasses.dataclass
class SocketParams:
    source_address = None
    proxy_type: int = None
    proxy_addr: str = None
    proxy_port: int = None
    proxy_rdns: bool = True
    proxy_username: str = None
    proxy_password: str = None
    socket_options: typing.Optional[typing.List[tuple]] = None

    @classmethod
    def socks5h(cls, host: str, port: int, username=None, password=None, rdns=True):
        return cls(
            proxy_type=socks.PROXY_TYPE_SOCKS5,
            proxy_addr=host,
            proxy_port=port,
            proxy_username=username,
            proxy_password=password,
            proxy_rdns=rdns,
        )

    @classmethod
    def from_socks5h(cls, socks5h: str):
        if not socks5h.startswith("socks5h://"):
            raise ValueError("socks5h must start with socks5h://")
        socks5h = socks5h[len("socks5h://"):]
        if "@" in socks5h:
            userinfo, hostinfo = socks5h.split("@", 1)
            if ":" in userinfo:
                username, password = userinfo.split(":", 1)
            else:
                username, password = userinfo, None
        else:
            hostinfo = socks5h
            username, password = None, None
        if ":" in hostinfo:
            host, port = hostinfo.split(":", 1)
            port = int(port)
        else:
            host, port = hostinfo, 1080
        return cls.socks5h(host, port, username, password)

    def kwargs(self):
        return {
            'source_address': self.source_address,
            'proxy_type'    : self.proxy_type,
            'proxy_addr'    : self.proxy_addr,
            'proxy_port'    : self.proxy_port,
            'proxy_rdns'    : self.proxy_rdns,
            'proxy_username': self.proxy_username,
            'proxy_password': self.proxy_password,
            'socket_options': self.socket_options
        }


class IMAP4Client(IMAP4):
    def __init__(self, host='', port=IMAP4_PORT, timeout=None, socket_params: SocketParams = None):
        self.socket_params = socket_params
        super().__init__(host, port, timeout)  # 3.9

    def open(self, host="", port=143, timeout=None):
        return super().open(host, port, timeout)

    def _create_socket(self, timeout):
        # Default value of IMAP4.host is '', but socket.getaddrinfo()
        # (which is used by socket.create_connection()) expects None
        # as a default value for host.

        host = None if not self.host else self.host
        sys.audit("imaplib.open", self, self.host, self.port)
        address = (host, self.port)
        if timeout is not None and not timeout:
            raise ValueError('Non-blocking socket (timeout=0) is not supported')
        if self.socket_params is None:
            return socket.create_connection(address, timeout)
        else:
            return socks.create_connection(address, **self.socket_params.kwargs())


class IMAP4SSLClient(IMAP4Client):
    def __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=None,
                 certfile=None, ssl_context=None, timeout=None, socket_params: SocketParams = None):
        if ssl_context is not None and keyfile is not None:
            raise ValueError("ssl_context and keyfile arguments are mutually "
                             "exclusive")
        if ssl_context is not None and certfile is not None:
            raise ValueError("ssl_context and certfile arguments are mutually "
                             "exclusive")
        if keyfile is not None or certfile is not None:
            import warnings
            warnings.warn("keyfile and certfile are deprecated, use a "
                          "custom ssl_context instead", DeprecationWarning, 2)
        self.keyfile = keyfile
        self.certfile = certfile
        if ssl_context is None:
            ssl_context = ssl._create_stdlib_context(  # noqa
                certfile=certfile,
                keyfile=keyfile
            )
        self.ssl_context = ssl_context
        super().__init__(host, port, timeout, socket_params)

    def _create_socket(self, timeout):
        sock = super()._create_socket(timeout)
        return self.ssl_context.wrap_socket(sock,
                                            server_hostname=self.host)

    def open(self, host='', port=IMAP4_SSL_PORT, timeout=None):
        """Setup connection to remote server on "host:port".
            (default: localhost:standard IMAP4 SSL port).
        This connection will be used by the routines:
            read, readline, send, shutdown.
        """
        super().open(host, port, timeout)
