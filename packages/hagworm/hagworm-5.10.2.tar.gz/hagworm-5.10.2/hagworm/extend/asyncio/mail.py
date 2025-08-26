# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import aiosmtplib

from email.message import EmailMessage

from .base import Utils


class EmailBody:

    def __init__(self, sender: str, recipients: typing.Sequence[str], message: EmailMessage):

        self._sender: str = sender
        self._recipients: typing.Sequence[str] = recipients
        self._message: EmailMessage = message

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def recipients(self) -> typing.Sequence[str]:
        return self._recipients

    @property
    def message(self) -> EmailMessage:
        return self._message

    @staticmethod
    def create_message(
            sender: str, recipients: typing.Sequence[str], subject: str,
            content: str, content_type: str = r'text/html'
    ) -> EmailMessage:

        message = EmailMessage()

        if not sender:
            message[r'From'] = sender

        if not recipients:
            message[r'To'] = recipients

        message[r'Subject'] = subject
        message.set_content(content)
        message.set_type(content_type)

        return message


class SMTPClient:

    def __init__(self, username: str, password: str, hostname: str, port: int, retry_count: int = 5, **kwargs):

        self._username: str = username
        self._password: str = password

        self._hostname: str = hostname
        self._port: int = port

        self._retry_count: int = retry_count

        self._smtp_settings: typing.Dict = kwargs

    @staticmethod
    def format_address(nickname: str, mailbox: str) -> str:

        return f'{nickname}<{mailbox}>'

    def format_addresses(self, addresses: typing.List[typing.Tuple[str, str]]) -> str:

        return r';'.join(self.format_address(*addr) for addr in addresses)

    # 发送多封邮件
    async def send_messages(self, email_body_list: typing.List[EmailBody]):

        resp = None

        try:

            async with aiosmtplib.SMTP(hostname=self._hostname, port=self._port, **self._smtp_settings) as client:

                await client.login(self._username, self._password)

                for email_body in email_body_list:

                    resp = await client.send_message(
                        email_body.message, sender=email_body.sender, recipients=email_body.recipients
                    )

                    Utils.log.info(f'{email_body.recipients} => {resp}')

        except aiosmtplib.SMTPException as err:

            Utils.log.error(err)

        return resp

    # 发送单封邮件
    async def send_message(self, sender: str, recipients: typing.Sequence[str], message: EmailMessage):

        return await self.send_messages(
            [EmailBody(sender, recipients, message)]
        )

    # 简单的发送
    async def send(self, sender: str, recipients: typing.Sequence[str], subject: str, content: str):

        return await self.send_message(
            sender, recipients,
            EmailBody.create_message(sender, recipients, subject, content)
        )
