# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from batrachomyomachia.utilities import read_pr_body


def test_read_pr_body():
    assert read_pr_body("") == ("", [])
    assert read_pr_body("No cc\n") == ("No cc\n", [])
    assert read_pr_body("No cc1\nNo cc2\n") == ("No cc1\nNo cc2\n", [])
    assert read_pr_body("cc: foo@bar.com ,baz@baz.com") == (
        "",
        [
            "foo@bar.com",
            "baz@baz.com",
        ],
    )
    assert read_pr_body(
        "Hello\ncc: not used\nbecause of this\n"
        "cc: 1@bar.com ,2@baz.com\n\ncc: 3@bar.com ,4@baz.com"
    ) == (
        "Hello\ncc: not used\nbecause of this\n",
        [
            "3@bar.com",
            "4@baz.com",
            "1@bar.com",
            "2@baz.com",
        ],
    )
