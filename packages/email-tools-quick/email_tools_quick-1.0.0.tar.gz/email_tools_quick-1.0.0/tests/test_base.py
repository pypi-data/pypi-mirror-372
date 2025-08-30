# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import os

import dotenv
import pytest

from email_tools_quick import CommonClient, MSClient
import json
import pathlib

dotenv.load_dotenv()
ADDRESS = os.environ["TESTBASEADDRESS"]  # noqa
PASSWORD = os.environ["TESTBASEPASSWORD"]  # noqa

A, P, C, R = os.environ["TEST_MS_MY"].split("----")


def test_login():
    client = CommonClient.login(ADDRESS, PASSWORD)
    with client:
        pass


def test_latest_emails():
    client = CommonClient.login(ADDRESS, PASSWORD)
    with client:
        for m in client.latest(10):
            print(m.date, m.subject)


def test_ms_login():
    cache = pathlib.Path(__file__).parent / ".cache"
    if cache.exists():
        access_token = json.loads(cache.read_text())["access_token"]
    else:
        access_token = MSClient.generate_access_token(R, C)
        cache.write_text(json.dumps(access_token))
        access_token = access_token["access_token"]
    client = MSClient.login(A, P, access_token=access_token)
    with client:
        for m in client.latest(10):
            print(m.date, m.subject)


if __name__ == '__main__':
    pytest.main([__file__])
