# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from unittest.mock import MagicMock, patch

import fakeredis
import platformdirs
import pytest
from git import BadName

from batrachomyomachia.local_git_ops import (
    GccGitDescrWays,
    ensure_local_clone,
    gcc_git_descr,
)


@pytest.fixture
def mock_redis(monkeypatch):
    fake = fakeredis.FakeRedis()
    monkeypatch.setattr("redis.from_url", lambda url, *a, **kw: fake)
    return fake


@pytest.fixture
def mock_redis_lock():
    with patch("redis.lock.Lock") as mock_lock_cls:
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_lock_cls.return_value = mock_lock
        yield mock_lock


@pytest.fixture
def mock_local_git_repo_path(monkeypatch):
    path_mock = MagicMock()

    def side_effect(owner, reponame):
        return str(
            platformdirs.user_cache_path(
                appname="local_git_ops_test", appauthor="batrachomyomachia"
            )
            / owner
            / reponame
        )

    path_mock.side_effect = side_effect
    return path_mock


def test_ensure_local_clone(mock_redis, mock_redis_lock, mock_local_git_repo_path):
    ensure_local_clone(
        owner="gcc",
        reponame="gcc-TEST",
    )


def test_gcc_descr(mock_redis, mock_redis_lock, mock_local_git_repo_path):
    repo = ensure_local_clone(
        owner="gcc",
        reponame="gcc-TEST",
    )

    with pytest.raises(BadName):
        gcc_git_descr(repo, "invalid sha", GccGitDescrWays.VANILLA)

    assert (
        gcc_git_descr(repo, "refs/tags/releases/gcc-4.9.4", GccGitDescrWays.VANILLA)
        == ""
    )
    assert (
        gcc_git_descr(repo, "refs/tags/releases/gcc-4.9.4", GccGitDescrWays.SHORT) == ""
    )
    assert (
        gcc_git_descr(repo, "refs/tags/releases/gcc-4.9.4", GccGitDescrWays.LONG) == ""
    )

    gcc16_basepoint_sha = "tags/basepoints/gcc-16"
    assert (
        gcc_git_descr(repo, gcc16_basepoint_sha, GccGitDescrWays.VANILLA)
        == "r16-0-g64e473c6561d75dce5da255cebba5215f7d644be"
    )
    assert gcc_git_descr(repo, gcc16_basepoint_sha, GccGitDescrWays.SHORT) == "r16-0"
    assert gcc_git_descr(repo, gcc16_basepoint_sha, GccGitDescrWays.LONG) == "r16"

    gcc15_basepoint_sha = "tags/basepoints/gcc-15"
    assert (
        gcc_git_descr(repo, gcc15_basepoint_sha, GccGitDescrWays.VANILLA)
        == "r15-0-g504c8a9afa3f752a17259ceab6e256ae448dc057"
    )
    assert gcc_git_descr(repo, gcc15_basepoint_sha, GccGitDescrWays.SHORT) == "r15-0"
    assert gcc_git_descr(repo, gcc15_basepoint_sha, GccGitDescrWays.LONG) == "r15"

    some_commit_in_gcc15 = "d056ac5fce4cf6de698b4e1e4fe266e5ebbd0530"
    assert (
        gcc_git_descr(repo, some_commit_in_gcc15, GccGitDescrWays.VANILLA)
        == "r15-9776-gd056ac5fce4cf6"
    )
    assert (
        gcc_git_descr(repo, some_commit_in_gcc15, GccGitDescrWays.SHORT) == "r15-9776"
    )
    assert (
        gcc_git_descr(repo, some_commit_in_gcc15, GccGitDescrWays.LONG)
        == "r15-9776-gd056ac5fce4cf6de698b4e1e4fe266e5ebbd0530"
    )
