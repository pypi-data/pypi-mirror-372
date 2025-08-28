# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from io import StringIO

from batrachomyomachia.utilities import dump

from .load import dict_from_yaml


def test_dump():
    # Check that round trip works
    # And that we write strings as multiline
    data = dict_from_yaml("sourceware-gcc-test-49.yml")
    output = StringIO()
    dump(data, output)
    assert (
        """description: The GNU Compiler Collection includes front ends for C, C++, \n"""
        """        Objective-C, Fortran, Ada, Go, D and Modula-2 as well as libraries for \n"""
        """        these languages (libstdc++,...).""" in output.getvalue()
    )
