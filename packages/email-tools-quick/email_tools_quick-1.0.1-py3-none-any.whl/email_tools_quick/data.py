# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import dataclasses
import datetime
import enum
from typing import TypedDict

import dateutil.parser
import dateutil.parser


class MSAccessToken(TypedDict):
    token_type: str
    scope: str
    expires_in: int
    ext_expires_in: int
    access_token: str
    refresh_token: str


class MSAccessTokenError(TypedDict):
    error: str
    error_description: str
    error_codes: list[int]
    timestamp: str
    trace_id: str
    correlation_id: str


@dataclasses.dataclass
class EMail:
    subject: str | None
    date: datetime.datetime | str | None
    body: str
    html: str | None = None
    sender: str | None = None
    folder_name: str = "INBOX"
    email_counter: int = 0

    def __getitem__(self, item):
        if item == "subject":
            return self.subject
        elif item == "date":
            return self.date
        elif item == "body":
            return self.body
        elif item == "email_counter":
            return self.email_counter
        elif item == "folder_name":
            return self.folder_name
        else:
            raise KeyError(f"Invalid key: {item}")

    def _date(self) -> str | None:
        if isinstance(self.date, datetime.datetime):
            return self.date.strftime("%Y-%m-%d %H:%M:%S %z")
        elif isinstance(self.date, str):
            return dateutil.parser.parse(self.date).astimezone(datetime.timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            )
        elif self.date is None:
            return None
        else:
            raise TypeError(f"Invalid date type: {type(self.date)}")

    def __iter__(self):
        yield from {
            "subject"      : self.subject,
            "date"         : self._date(),
            "body"         : self.body,
            "email_counter": self.email_counter,
            "folder_name"  : self.folder_name
        }.items()

    def __str__(self) -> str:
        return "\n".join([
            "=" * 37,
            f"Subject: {self.subject}",
            f"Date: {self._date()}",
            f"Sender: {self.sender if self.sender else 'Unknown'}",
            "",
            f"{self.body}",
            "=" * 37,
        ])


@dataclasses.dataclass
class MailBoxMap:
    INBOX: str = "INBOX"
    Sent: str = "Sent"
    Trash: str = "Trash"
    Junk: str = "Junk"
    Drafts: str = "Drafts"
    Archive: str = "Archive"

    @property
    def send(self):
        return "发件箱"

    @property
    def trash(self):
        return "回收站"

    @property
    def junk(self):
        return "垃圾箱"

    @property
    def drafts(self):
        return "草稿箱"

    @property
    def archive(self):
        return "归档箱"


class MailBox(enum.Enum):
    INBOX = "INBOX"
    Sent = "Sent"
    Trash = "Trash"
    Junk = "Junk"
    Drafts = "Drafts"
    Archive = "Archive"

    def mailbox(self, mailbox_map: MailBoxMap):
        if self == MailBox.INBOX:
            return mailbox_map.INBOX
        elif self == MailBox.Sent:
            return mailbox_map.Sent
        elif self == MailBox.Trash:
            return mailbox_map.Trash
        elif self == MailBox.Junk:
            return mailbox_map.Junk
        elif self == MailBox.Drafts:
            return mailbox_map.Drafts
        elif self == MailBox.Archive:
            return mailbox_map.Archive
        else:
            raise ValueError(f"Invalid mailbox: {self}")
