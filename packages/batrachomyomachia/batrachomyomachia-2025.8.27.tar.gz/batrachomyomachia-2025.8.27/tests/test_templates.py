# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from datetime import datetime

from git import DiffIndex
from pyforgejo import PullRequest

from batrachomyomachia.forgejo_api_ops import PullRequestVersion
from batrachomyomachia.templates import (
    get_template,
    pr_cover,
    pr_summary_email_subject,
    pr_summary_email_text,
    pr_versions_text,
    pr_welcome_text,
)

from .load import dict_from_yaml


def test_get_template():
    assert get_template("pr-versions.j2") is not None


def test_pr_cover():
    cover = pr_cover(
        listname="Some list",
        author="alfierichards@sourceware.org",
        created_at=datetime.fromisoformat("2025-04-03 12:06:42+00:00"),
        updated_at=datetime.fromisoformat("2025-05-21 13:56:44+00:00"),
        base_repo_full_name="gcc/gcc-TEST",
        base_gcc_descr="",
        base_ref="master",
        base_sha="4e47e2f833732c5d9a3c3e69dc753f99b3a56737",
        merge_base="f99017c3125f4400cf6a098cf5b33d32fe3e6645",
        head_repo_full_name="alfie.richards/gcc-TEST",
        head_gcc_descr="",
        head_ref="fmv_cxx",
        head_sha="b47c31eaa3f42a720b635b4dc050959703ca82c5",
        changed_files=93,
        additions=2727,
        deletions=922,
        diff=DiffIndex(),
        pr_body="Another update to this series.",
        pr_diff_url="https://forge.sourceware.org/gcc/gcc-TEST/pulls/49.diff",
        pr_html_url="https://forge.sourceware.org/gcc/gcc-TEST/pulls/49",
        requested_reviewers=["rsandifo", "rearnsha"],
    )
    assert "alfierichards@sourceware.org has requested" in cover
    assert "Created on: 2025-04-03 12:06:42+00:00" in cover
    assert "Latest update: 2025-05-21 13:56:44+00:00" in cover
    assert "Changes: 93 changed files, 2727 additions, 922 deletions" in cover
    assert (
        "Head revision: alfie.richards/gcc-TEST ref fmv_cxx commit b47c31eaa3f42a720b635b4dc050959703ca82c5"
        in cover
    )
    assert (
        "Base revision: gcc/gcc-TEST ref master commit 4e47e2f833732c5d9a3c3e69dc753f99b3a56737"
        in cover
    )
    assert "Merge base: f99017c3125f4400cf6a098cf5b33d32fe3e6645" in cover
    assert (
        "Full diff url: https://forge.sourceware.org/gcc/gcc-TEST/pulls/49.diff"
        in cover
    )
    assert "Discussion:  https://forge.sourceware.org/gcc/gcc-TEST/pulls/49" in cover
    assert "Requested Reviewers: rsandifo, rearnsha" in cover
    assert "Another update to this series." in cover


def test_pr_summary_email_text():
    pr = PullRequest(**dict_from_yaml("minimal.yml"))
    t = pr_summary_email_text(pr)
    assert "Created on: 2025-04-03 12:06:42+00:00" in t
    assert "Latest update: 2025-05-21 13:56:44+00:00" in t
    assert "Author: alfierichards@sourceware.org" in t
    assert "Changes: 93 changed files, 2727 additions, 922 deletions" in t
    assert (
        "Head revision: alfie.richards/gcc-TEST ref fmv_cxx commit b47c31eaa3f42a720b635b4dc050959703ca82c5"
        in t
    )
    assert (
        "Base revision: gcc/gcc-TEST ref master commit 4e47e2f833732c5d9a3c3e69dc753f99b3a56737"
        in t
    )
    assert "Merge base: f99017c3125f4400cf6a098cf5b33d32fe3e6645" in t
    assert "Full diff url: https://forge.sourceware.org/gcc/gcc-TEST/pulls/49.diff" in t
    assert "Discussion:  https://forge.sourceware.org/gcc/gcc-TEST/pulls/49" in t
    assert "Requested Reviewers: rsandifo, rearnsha" in t
    assert "Another update to this series" in t


def test_pr_summary_email_subject():
    pr = PullRequest(**dict_from_yaml("minimal.yml"))
    t = pr_summary_email_subject(pr)
    assert "[gcc/gcc-TEST] #49 FMV refactor and ACLE compliance for C++" == t


def test_pr_versions_text():
    t = pr_versions_text(
        repo_url="http://site/org/repo",
        pr_index=42,
        versions=[
            PullRequestVersion(version=1, base_ref="abc", head_ref="def"),
            PullRequestVersion(version=2, base_ref="ghi", head_ref="jhk"),
        ],
    )
    assert "| 1 | abc | def |" in t
    assert "[(diff)](http://site/org/repo/compare/abc...def)" in t
    assert "| 2 | ghi | jhk |" in t
    assert "[(diff)](http://site/org/repo/compare/ghi...jhk)" in t
    assert "PR=42" in t


def test_pr_welcome_text():
    t = pr_welcome_text(
        sitename="our lovely site",
        username="j.hacker",
        site_help_resources="Say hi",
        repository_help_resources="Say a prayer",
        repository_patch_guidelines="Two ducks in a row",
    )
    assert "Welcome to our lovely site" in t
    assert "Hi @j.hacker" in t
    assert "\n\nSay hi" in t
    assert "\n\nSay a prayer\n\n" in t
    assert "\n\nTwo ducks in a row\n\n" in t
