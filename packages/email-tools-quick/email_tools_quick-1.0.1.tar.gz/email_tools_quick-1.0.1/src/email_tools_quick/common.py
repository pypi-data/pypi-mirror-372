# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from typing import Union

from email_tools_quick.base import BaseEmailClient
from email_tools_quick.mail import IMAP4Client
from email_tools_quick.mail import IMAP4SSLClient
from email_tools_quick.mail import IMAP4_PORT
from email_tools_quick.mail import IMAP4_SSL_PORT
from email_tools_quick.mail import SocketParams
from email_tools_quick.mixin import EmailMixin


class CommonClient(BaseEmailClient, EmailMixin):
    def __init__(self, client: Union[IMAP4Client, IMAP4SSLClient]):
        super().__init__()
        self.client = client

    @classmethod
    def login(
            cls,
            address: str,
            password: str,
            host: str = None,
            port: int = None,
            use_ssl: bool = True,
            socket_params: SocketParams = None,
            **kwargs,
    ):
        host = host or cls.get_host(address)
        if use_ssl:
            port = port or IMAP4_SSL_PORT
            client = IMAP4SSLClient(host, port, socket_params=socket_params)
        else:
            port = port or IMAP4_PORT
            client = IMAP4Client(host, port, socket_params=socket_params)
        client.login(address, password)
        return cls(client)
