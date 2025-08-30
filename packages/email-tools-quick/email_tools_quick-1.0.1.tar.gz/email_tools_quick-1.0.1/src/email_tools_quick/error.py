# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""


class BaseEmailError(Exception):
    def __init__(self, msg: str, e: Exception = None):
        super().__init__(f"{msg}: {e}")


class LoginEmailError(BaseEmailError):
    """
    Exception raised for errors in the login process.
    """


class FetchEmailError(BaseEmailError):
    """
    Exception raised for errors in fetching emails.
    """
