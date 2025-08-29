#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Utility functions for fetching and sending emails.

Usage:
from xenoslib.mail import MailFetcher, SMTPMail

# Fetch emails
for email_data in MailFetcher(imap_server, mail_addr, mail_pwd, interval=30, days=30):
    print(email_data["subject"])

# Send email
sender = SMTPMail(smtp_server, sender, password, port=25)
sender.send(subject, message, receiver, cc, bcc, filename)

"""
import os
import datetime
from time import sleep
import logging
from collections import deque
import smtplib
import email
from email.mime.text import MIMEText
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid

from imapclient import IMAPClient


logger = logging.getLogger(__name__)


class MailFetcher:
    """
    Fetch emails from mail inbox using IMAP protocol.
    """

    def __new__(
        cls,
        imap_server,
        mail_addr,
        mail_pwd,
        interval=30,
        days=1,
        timeout=30,
        skip_current=True,
        endless=True,
    ):
        self = super().__new__(cls)
        self.imap_server = imap_server
        self.mail_addr = mail_addr
        self.mail_pwd = mail_pwd
        self.days = days
        self.timeout = timeout

        self.msg_ids = deque(maxlen=999)
        if not endless:
            skip_current = False
        if skip_current:  # mark and skip current mails
            logger.debug("Skipping existing emails...")
            mails = self.fetch_emails()
            self.msg_ids.extend(mails.keys())
        return self.fetching(interval=interval, endless=endless)

    def fetching(self, interval=30, endless=True):
        """Continuously fetch emails at the specified interval."""
        logger.debug("Start checking emails...")
        while True:
            yield from self.parse_emails(self.fetch_emails())
            if not endless:
                break
            sleep(interval)

    def parse_emails(self, emails):
        for msg_id, msg in emails.items():
            if msg_id in self.msg_ids:
                continue
            body = email.message_from_bytes(msg[b"BODY[]"])
            subject = str(email.header.make_header(email.header.decode_header(body["Subject"])))
            payload = body.get_payload(decode=True)
            if body.is_multipart():
                for part in body.walk():
                    if "text/html" in part.get_content_type():
                        payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                try:
                    payload = payload.decode()
                except UnicodeDecodeError:
                    payload = payload.decode("latin1")  # failover decode
            body["raw"] = msg[b"BODY[]"]
            body["subjectx"] = subject
            body["payload"] = payload
            body["internal_date"] = msg[b"INTERNALDATE"]
            yield body
            self.msg_ids.append(msg_id)

    def fetch_emails(self):
        """Login and fetch emails."""
        from_date = datetime.datetime.today() - datetime.timedelta(days=self.days)
        logger.debug(f"Fetching emails since {from_date:%Y-%m-%d %H:%M:%S} ({self.days} days ago)")
        for i in range(5):
            try:
                with IMAPClient(self.imap_server, timeout=self.timeout) as client:
                    client.login(self.mail_addr, self.mail_pwd)
                    client.select_folder("INBOX", readonly=True)
                    messages = client.search(["SINCE", from_date])
                    emails = client.fetch(messages, ["INTERNALDATE", "BODY.PEEK[]"])
                    return emails
            except Exception as exc:
                logger.warning(exc)
                sleep(30)
        raise Exception(
            "Reached maximum retry attempts when connect IMAP server. Giving up connection."
        )


class SMTPMail:
    def __init__(self, smtp_server="", sender="", password="", port=25):
        self.smtp_server = smtp_server
        self.port = int(port)
        self.sender = sender
        self.password = password
        if self.port == 465:  # use SSL by port
            self.SMTP = smtplib.SMTP_SSL
        else:
            self.SMTP = smtplib.SMTP

    def send(
        self, subject, message, receiver=None, receivers=None, cc=None, bcc=None, filename=None
    ):
        if receivers is None:
            receivers = []
        if isinstance(receiver, str):
            receivers.append(receiver)
        elif isinstance(receiver, (list, tuple)):
            receivers.extend(receiver)
        msg = self.construct_msg(
            subject=subject,
            message=message,
            receivers=receivers,
            cc=cc,
            filename=filename,
        )
        if cc:
            msg["Cc"] = ";".join(cc)
            receivers.extend(cc)
        if bcc:
            receivers.extend(bcc)
        with self.SMTP(self.smtp_server, self.port) as smtp:
            if smtp.has_extn("STARTTLS"):
                smtp.starttls()
            try:
                smtp.login(self.sender, self.password)
            except Exception as exc:
                logger.warning(exc)
                return False
            smtp.sendmail(self.sender, receivers, msg.as_string())
            return True

    def construct_msg(self, subject, message, receivers=None, cc=None, filename=None):
        msg = MIMEMultipart()
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = Header(self.sender, "utf-8")
        msg["To"] = ";".join(receivers)
        msg["Message-ID"] = make_msgid()
        msg.attach(MIMEText(message, "html", "utf-8"))
        if filename:
            attachment = MIMEApplication(open(filename, "rb").read())
            attachment.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(attachment)
        return msg


def test_imap():
    try:
        import env  # noqa
    except ModuleNotFoundError:
        pass
    imap_server = os.environ["IMAP_SERVER"]
    mail_addr = os.environ["IMAP_ADDR"]
    mail_pwd = os.environ["IMAP_PASS"]
    for email_data in MailFetcher(
        imap_server, mail_addr, mail_pwd, interval=1, days=1, skip_current=False
    ):
        # ~ print(email_data["subject"])
        print(email_data["subjectx"])
        print(email_data["payload"])
        # ~ print(email_data.keys())


def test_smtp():
    try:
        import env  # noqa
    except ModuleNotFoundError:
        pass
    mail_addr = os.environ["SMTP_ADDR"]
    mail_pwd = os.environ["SMTP_PASS"]
    smtp_server = os.environ["SMTP_SERVER"]
    subject = "Test Email2"
    message = '<span style="color:red">This is a test email.</span>'
    email_sender = SMTPMail(smtp_server, sender=mail_addr, password=mail_pwd, port=465)
    # email_sender = SMTPMail(smtp_server, sender=mail_addr, password=mail_pwd, port=587)
    # ~ email_sender.send(subject=subject, message=message, receiver=os.environ["RECEIVER"],bcc=["haiwe.lu@sap.com"])
    email_sender.send(
        subject=subject, message=message, receiver="luhw@cndatacom.com", bcc=["haiwei.lu@sap.com"]
    )


if __name__ == "__main__":
    # ~ test_imap()
    test_smtp()
