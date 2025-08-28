# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from batrachomyomachia.forgejo_api_ops import extract_pr_components


def test_extract_pr_components(caplog):
    with caplog.at_level("ERROR"):
        caplog.clear()
        assert (
            extract_pr_components(
                "https://codeberg.org/",
            )
            is None
        )
        assert "must be in the form" in caplog.text

    with caplog.at_level("ERROR"):
        caplog.clear()
        assert (
            extract_pr_components(
                "https://codeberg.org/forgejo/forgejo/pulls/8040/extra",
            )
            is None
        )
        assert "must be in the form" in caplog.text

    with caplog.at_level("ERROR"):
        caplog.clear()
        assert (
            extract_pr_components(
                "https://codeberg.org/forgejo/forgejo/issues/8040",
            )
            is None
        )
        assert "must be in the form" in caplog.text

    with caplog.at_level("ERROR"):
        caplog.clear()
        assert (
            extract_pr_components(
                "https://codeberg.org/forgejo/forgejo/pulls/notanumber",
            )
            is None
        )
        assert "must be in the form" in caplog.text

    assert extract_pr_components(
        "https://codeberg.org/someorg/somerepo/pulls/1122",
    ) == ("someorg", "somerepo", 1122)
