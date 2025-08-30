# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from .common import CommonClient
from .data import EMail
from .data import MailBox
from .data import MailBoxMap
from .error import BaseEmailError
from .error import FetchEmailError
from .error import LoginEmailError
from .mail import IMAP4Client
from .mail import IMAP4SSLClient
from .mail import IMAP4_PORT
from .mail import IMAP4_SSL_PORT
from .mail import SocketParams
from .ms import MSClient

__version__ = '1.0.1'

__all__ = [
    "CommonClient",
    "MSClient",

    "BaseEmailError",
    "LoginEmailError",
    "FetchEmailError",
]
