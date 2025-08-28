# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from unittest.mock import Mock, patch

from dynaconf import Dynaconf  # type: ignore[import]

from batrachomyomachia.webhook import deal_with

TEST_SETTINGS = Dynaconf(
    forgejo_url="https://forge",
    publish_to="some@one.com",
    repositories=[
        {
            "owner": "some_org",
            "name": "foo",
        }
    ],
)


@patch("batrachomyomachia.config.settings", TEST_SETTINGS)
@patch(
    "batrachomyomachia.webhook.handle_comment_created_submit",
    new_callable=Mock,
)
def test_deal_with_issue_comment_submit(mock_submit):
    mock_submit.return_value = "submit result"
    payload = {"action": "created", "comment": {"body": "/submit"}}
    assert deal_with("issue_comment", "dummy", payload)
    mock_submit.assert_called_once_with(payload)


@patch("batrachomyomachia.config.settings", TEST_SETTINGS)
@patch(
    "batrachomyomachia.webhook.handle_comment_created_allow",
    new_callable=Mock,
)
def test_deal_with_issue_comment_allow(mock_allow):
    mock_allow.return_value = "allow result"
    payload = {"action": "created", "comment": {"body": "/allow\n"}}
    assert deal_with("issue_comment", "dummy", payload)
    mock_allow.assert_called_once_with(payload)


@patch("batrachomyomachia.config.settings", TEST_SETTINGS)
@patch(
    "batrachomyomachia.webhook.handle_comment_created_preview",
    new_callable=Mock,
)
def test_deal_with_issue_comment_preview(mock_preview):
    mock_preview.return_value = "preview result"
    payload = {"action": "created", "comment": {"body": " /preview\n"}}
    assert deal_with("issue_comment", "dummy", payload)
    mock_preview.assert_called_once_with(payload)


@patch("batrachomyomachia.config.settings", TEST_SETTINGS)
@patch("batrachomyomachia.webhook.handle_pr_opened", new_callable=Mock)
def test_deal_with_pr_opened(mock_opened):
    mock_opened.return_value = "pr opened"
    payload = {"action": "opened"}
    assert deal_with("pull_request", "dummy", payload)
    mock_opened.assert_called_once_with(payload)


def test_deal_with_irrelevant_event():
    payload = {"action": "edited", "comment": {"body": "   /submit\n"}}
    result = deal_with("issue_comment", "dummy", payload)
    assert not result


def test_deal_with_non_command_comment():
    payload = {"action": "created", "comment": {"body": "Just a comment."}}
    result = deal_with("issue_comment", "dummy", payload)
    assert not result


def test_deal_with_unknown_event():
    payload = {"action": "opened"}
    result = deal_with("push", "dummy", payload)
    assert not result


def test_deal_with_pr_closed():
    payload = {"action": "closed"}
    result = deal_with("pull_request", "dummy", payload)
    assert not result
