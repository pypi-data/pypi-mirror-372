# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.


from unittest.mock import mock_open, patch

import fakeredis
import pytest

from batrachomyomachia.allowlist import (
    allow_user_submit,
    dump_can_submit_list,
    update_redis_list,
    user_can_submit,
)


@pytest.fixture
def mock_redis(monkeypatch):
    fake = fakeredis.FakeRedis()
    monkeypatch.setattr("redis.from_url", lambda url, *a, **kw: fake)
    return fake


@pytest.fixture
def mock_allowed_users_path(tmp_path):
    test_file = tmp_path / "allowed_users.yaml"
    test_file.touch()  # Ensure the file exists
    with patch(
        "batrachomyomachia.allowlist.allowed_users_path", return_value=test_file
    ):
        yield test_file


def test_allow_user_submit_adds_user(mock_redis):
    allow_user_submit("alice")
    assert mock_redis.sismember("allow_user_submit", "alice")


def test_user_can_submit_true(mock_redis):
    mock_redis.sadd("allow_user_submit", "bob")
    assert user_can_submit("bob") is True


def test_user_can_submit_false(mock_redis):
    assert user_can_submit("bob") is False


def test_dump_can_submit_list(mock_redis, mock_allowed_users_path):
    mock_redis.sadd("allow_user_submit", "alice", "bob")
    with patch("builtins.open", mock_open()):
        with patch("batrachomyomachia.allowlist.dump") as dump_mock:
            dump_can_submit_list()
            dump_mock.assert_called_once()
            written_data = dump_mock.call_args[0][0]
            assert sorted(written_data) == ["alice", "bob"]


def test_update_redis_list(mock_redis, mock_allowed_users_path):
    mock_redis.sadd("allow_user_submit", "alice", "bob")
    yaml_content = "- alice\n- carol\n"
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        with patch("ruamel.yaml.YAML.load", return_value=["alice", "carol"]):
            update_redis_list()
    assert not mock_redis.sismember("allow_user_submit", "bob")
    assert mock_redis.sismember("allow_user_submit", "carol")
