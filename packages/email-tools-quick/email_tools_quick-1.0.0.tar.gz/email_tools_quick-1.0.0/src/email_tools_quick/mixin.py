# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import datetime
import re
from typing import Generator
from typing import Literal

from curl_cffi import requests
from loguru import logger

from email_tools_quick.data import EMail
from email_tools_quick.data import MSAccessToken
from email_tools_quick.data import MSAccessTokenError
from email_tools_quick.data import MailBox
from email_tools_quick.data import MailBoxMap
from email_tools_quick.error import FetchEmailError
from email_tools_quick.error import LoginEmailError
from email_tools_quick.mail import IMAP4Client
from email_tools_quick.mail import IMAP4SSLClient
from email_tools_quick.utils import parse_msg

TenantID = Literal['common', 'organizations', 'consumers']


class MSMixin:
    @staticmethod
    def generate_access_token(
            refresh_token: str,
            client_id: str,
            tenant_id: TenantID = 'common',
            **kwargs
    ) -> MSAccessToken:
        refresh_token_data = {
            'grant_type'   : 'refresh_token',
            'refresh_token': refresh_token,
            'client_id'    : client_id,
            **kwargs,
        }
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        try:
            response = requests.post(token_url, data=refresh_token_data)
        except Exception as e:
            raise LoginEmailError("获取 Access Token 失败: 网络请求异常") from e
        logger.info(response.text)
        if response.status_code == 200:
            response_json: MSAccessToken | MSAccessTokenError = response.json()
            if not response_json.get("access_token"):
                response_json: MSAccessTokenError
                error = response_json["error"]
                error_description = response_json["error_description"]
                error_codes = response_json["error_codes"]
                error_codes_str = ', '.join(map(str, error_codes))
                raise LoginEmailError(
                    "获取AccessToken失败",
                    e=Exception(f"[{error_codes_str}]{error}({error_description})")
                )
            return response_json
        else:
            raise LoginEmailError(f"获取 Access Token 失败: {response.status_code} - {response.status_code}")


class BaseMixin:
    client: IMAP4Client | IMAP4SSLClient

    @staticmethod
    def _get_host(qname: str) -> str:
        from dns.resolver import resolve
        from dns.exception import DNSException
        try:
            mx_records = resolve(qname, 'MX')
            return str(mx_records[0].exchange).rstrip('.')
        except DNSException as e:
            raise ValueError(f"DNS resolution failed for {qname}: {e}")

    @classmethod
    def get_host(cls, email: str) -> str:
        domain = email.split('@')[1]
        return cls._get_host(domain)

    def mailboxes(self):
        mbox_map = MailBoxMap()
        status, mailboxes = self.client.list(pattern="%")
        if status == "OK":
            for mbox in mailboxes:
                mbox: bytes
                try:
                    mbox: str = mbox.decode(encoding="utf-8")
                except UnicodeDecodeError:
                    logger.warning("邮箱名称解码失败，尝试使用 IMAP UTF-7 解码。")
                    continue
                mbox_ = re.search(r"\((.*)\) \"(.+)\" \"?([^\"]*)", mbox)
                flags = mbox_.group(1).strip(" ")
                nane = mbox_.group(3)
                for flag in ["\Sent", "\Trash", "\Junk", "\Drafts", "\Archive"]:
                    if flag in flags:
                        if flag == "\Sent":
                            mbox_map.Sent = nane
                        elif flag == "\Trash":
                            mbox_map.Trash = nane
                        elif flag == "\Junk":
                            mbox_map.Junk = nane
                        elif flag == "\Drafts":
                            mbox_map.Drafts = nane
                        elif flag == "\Archive":
                            mbox_map.Archive = nane
                        else:
                            logger.warning("未知邮箱标志: {flag}")
        return mbox_map

    def select(self, folder: str):
        logger.info(f"select {folder}")
        status, msg = self.client.select(folder, readonly=True)
        if status != "OK":
            raise FetchEmailError(f"选择邮箱失败({status},{msg})")

    def search(self, *criteria):
        status, messages = self.client.uid('search', None, *criteria)
        if status != 'OK':
            return []
        return messages[0].split()

    def ids(self, mbox: str, *criteria) -> list[bytes]:
        self.select(mbox)
        return self.search(*criteria)

    def fetch(self, mid: bytes):
        status, msg_data = self.client.uid('fetch', mid, '(RFC822)')
        if status != "OK":
            raise FetchEmailError(f"获取邮件失败({status})")
        return parse_msg(msg_data)

    def _query(self, folder: str, x='ALL'):
        status, message = self.client.select(folder)
        if status != 'OK':
            message = message[0]
            if message == b"No such mailbox":
                raise FetchEmailError(f"邮箱不存在或无法访问,请检查邮箱名称是否正确({folder}))")
            logger.warning(message)
            return []
        status, messages = self.client.uid('search', None, x)
        if status != 'OK':
            print(message)
            return []
        return messages[0].split()

    def mails(self, mbox: MailBox, *criteria, start=None, end=None, reverse=False) -> Generator[EMail, None, None]:
        maps = self.mailboxes()
        mbox_name = mbox.mailbox(maps)
        self.select(mbox_name)
        ids = self.search(*criteria)
        if reverse:
            ids = reversed(ids)
        if start is not None and end is not None:
            ids = ids[start:end]
        elif start is not None:
            ids = ids[start:]
        elif end is not None:
            ids = ids[:end]
        for mid in ids:
            yield self.fetch(mid)


class EmailBoxMixin(BaseMixin):
    client: IMAP4Client | IMAP4SSLClient

    def __iter__(self) -> Generator[EMail, None, None]:
        for email_data in self.inbox():
            yield email_data
        for email_data in self.junk():
            yield email_data

    def inbox(self, start: int = None, end: int = None) -> Generator[EMail, None, None]:
        for m in self.mails(MailBox.INBOX, "ALL", start=start, end=end):
            yield m

    def junk(self, start: int = None, end: int = None) -> Generator[EMail, None, None]:
        for m in self.mails(MailBox.Junk, "ALL", start=start, end=end):
            yield m


class EmailMixin(EmailBoxMixin):
    client: IMAP4Client | IMAP4SSLClient

    def latest(self, count: int) -> Generator[EMail, None, None]:
        for i in self.mails(MailBox.INBOX, "ALL", start=-count):
            yield i
        for i in self.mails(MailBox.Junk, "ALL", start=-count):
            yield i

    def latest_minutes(self, minutes: int) -> Generator[EMail, None, None]:
        now = datetime.datetime.now(datetime.timezone.utc)
        since = now - datetime.timedelta(minutes=minutes)
        since_date = since.strftime("%d-%b-%Y")
        criteria = [f"(SINCE {since_date})"]
        for i in self.mails(MailBox.INBOX, *criteria, reverse=True):
            if (now - i.date).total_seconds() / 60 <= minutes:
                yield i
        for i in self.mails(MailBox.Junk, *criteria, reverse=True):
            if (now - i.date).total_seconds() / 60 <= minutes:
                yield i
