# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import imaplib
from abc import ABC
from abc import abstractmethod

from email_tools_quick.mail import IMAP4Client
from email_tools_quick.mail import IMAP4SSLClient
from email_tools_quick.mail import SocketParams


class BaseEmailClient(ABC):
    client: IMAP4Client | IMAP4SSLClient

    @classmethod
    @abstractmethod
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
        pass

    def logout(self):
        try:
            self.client.logout()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error):
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
        return False
