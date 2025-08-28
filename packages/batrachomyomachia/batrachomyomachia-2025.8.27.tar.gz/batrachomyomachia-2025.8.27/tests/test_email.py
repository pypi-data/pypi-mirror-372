# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from email.message import EmailMessage
from unittest.mock import MagicMock, patch

from pyforgejo import PullRequest, PyforgejoApi

from batrachomyomachia.email import send_pr_summary_mail
from batrachomyomachia.utilities import PullRequestData

from .load import dict_from_yaml

# def test_mail_from():
#     assert len(mail_from(dict_from_yaml("minimal.yml"))) == 2


@patch("smtplib.SMTP")
def test_send_pr_summary_mail_no_ssl_no_html(mock_smtp: MagicMock):
    m = MagicMock()
    mock_smtp.return_value = m
    pr = PullRequest(**dict_from_yaml("minimal.yml"))
    data = PullRequestData(
        "url",
        "owner",
        "repo",
        1,
        PyforgejoApi(base_url="http://localhost", api_key="api_key"),
        pr,
        "body",
        [],
    )
    smtp = {
        "host": "smtp.com",
        "port": 25,
        "ssl": False,
        "tls": False,
        "debug": False,
        "user": "me@me.com",
        "password": "pass",
    }

    send_pr_summary_mail(
        toaddr=["you <you@you.com>"],
        prdata=data,
        smtp=smtp,
    )

    mock_smtp.assert_called_with("smtp.com", 25)
    m.set_debuglevel.assert_called_with(0)
    m.starttls.assert_not_called()
    m.login.assert_called_with("me@me.com", "pass")
    a, _ = m.send_message.call_args
    message: EmailMessage = a[0]
    assert not message.is_multipart()
    m.quit.assert_called_once()
