# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from typing import Callable

from email_tools_quick.common import CommonClient
from email_tools_quick.mail import IMAP4SSLClient
from email_tools_quick.mail import IMAP4_SSL_PORT
from email_tools_quick.mail import SocketParams
from email_tools_quick.mixin import MSMixin


class MSClient(CommonClient, MSMixin):
    HOST: str = "outlook.office365.com"
    PORT: int = IMAP4_SSL_PORT

    @staticmethod
    def generate_auth_string(address: str, access_token: str) -> Callable[[bytes], str]:
        return lambda _: f"user={address}\1auth=Bearer {access_token}\1\1"

    @classmethod
    def login(
            cls,
            address: str,
            password: str,
            host: str = None,
            port: int = None,
            use_ssl: bool = True,
            socket_params: SocketParams = None,
            client_id: str = None,
            refresh_token: str = None,
            access_token: str = None,
            **kwargs,
    ):
        if access_token is None:
            if refresh_token is None or client_id is None:
                raise ValueError("如果没有 access_token, 则必须提供 refresh_token 和 client_id")
            access_token = cls.generate_auth_string(refresh_token, client_id)
        else:
            access_token = {"access_token": access_token}
        host = host or cls.HOST
        port = port or cls.PORT
        client = IMAP4SSLClient(host, port, socket_params=socket_params)
        authobject = cls.generate_auth_string(address, access_token["access_token"])
        client.authenticate('XOAUTH2', authobject)  # noqa
        return cls(client)
