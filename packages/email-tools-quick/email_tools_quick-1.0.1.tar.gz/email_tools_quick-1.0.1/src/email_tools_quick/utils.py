# -*- coding: utf-8 -*-
# Copyright (C) 2025 Cosmic-Developers-Union (CDU), All rights reserved.

"""Models Description

"""
import contextlib
import datetime
import email
import email.header
import email.message
import email.parser
import email.policy

import dateutil.parser
from bs4 import BeautifulSoup

from email_tools_quick.data import EMail


def decode_mime_words(s):
    decoded_fragments = email.header.decode_header(s)
    return ''.join([str(t[0], t[1] or 'utf-8') if isinstance(t[0], bytes) else t[0] for t in decoded_fragments])


def strip_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(strip=True)


def safe_decode(byte_content):
    # result = chardet.detect(byte_content)
    # encoding = result['encoding']
    # if encoding is not None:
    #     return byte_content.decode(encoding)
    # else:
    return byte_content.decode('utf-8', errors='ignore')


def remove_extra_blank_lines(text):
    lines = text.splitlines()
    # 使用 filter 删除空行，保留非空行
    return "\n".join(filter(lambda line: line.strip(), lines))


def parse_part(part: email.message.Message) -> str:
    contents = []
    content_type = part.get_content_type()
    content_disposition = str(part.get("Content-Disposition"))

    if "attachment" not in content_disposition:
        # logger.debug(f"{content_type=} | {content_disposition=}")
        if content_type == "text/plain":
            contents.append(safe_decode(part.get_payload(decode=True)))
        elif content_type == "text/html":
            html_content = safe_decode(part.get_payload(decode=True))
            contents.append(strip_html(html_content))
        else:
            pass
            # logger.warning(f"Unsupported content type: {content_type}")
    else:
        pass
        # logger.warning(f"attachment found: {content_disposition}")
    return "\n".join(contents)


def parse_html(raw: bytes):
    msg = email.message_from_bytes(raw)
    contents = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/html" and "attachment" not in content_disposition:
                contents.append(part.get_content())
    else:
        if msg.get_content_type() == "text/html":
            contents.append(msg.get_content())
    return "\n".join(contents)


def parse_msg(msg_data):
    """
    RFC 822
    :param msg_data:
    :return:
    """
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    body = []
    if msg.is_multipart():
        for part in msg.walk():
            body.append(parse_part(part))
    else:
        body.append(parse_part(msg))
    body = "\n".join(body)
    html = body
    with contextlib.suppress(Exception):
        html = parse_html(raw_email) or body
    return EMail(
        subject=msg["subject"].strip(),
        date=dateutil.parser.parse(msg["date"]).astimezone(datetime.timezone.utc),
        body=body,
        html=html,
        sender=msg["from"],
    )
