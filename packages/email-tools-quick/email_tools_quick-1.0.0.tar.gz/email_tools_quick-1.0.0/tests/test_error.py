# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
from curl_cffi import requests

from email_tools_quick import LoginEmailError


def test_raise_from():
    try:
        try:
            _ = requests.post("")
        except Exception as e:
            raise LoginEmailError("", e) from e
    except LoginEmailError as e:
        print(e)


if __name__ == '__main__':
    test_raise_from()
