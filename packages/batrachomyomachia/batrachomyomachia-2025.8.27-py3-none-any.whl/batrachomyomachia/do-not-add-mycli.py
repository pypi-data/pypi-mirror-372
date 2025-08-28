# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import logging

import click

from batrachomyomachia.config import (
    settings,
)
from batrachomyomachia.forgejo_api_ops import (
    post_pr_comment,
    pr_data_from_url,
)


@click.group()
def cli():
    """Configure logging for all commands."""
    logging.basicConfig(
        level=logging.getLevelNamesMapping()[settings["loglevel"].upper()],
        format=settings["log_format"],
    )


@click.command(help="Freeze a pull request into a new version.")
@click.option("--pr", required=True, help="Pull request URL")
@click.option("--text", help="content")
@click.option("--update", help="header")
def message(pr, text, update):
    logging.info(f"Freezing the current version of {pr}.")
    data = pr_data_from_url(pr)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr}.")
    post_pr_comment(data.client, data.owner, data.repo, data.index, text, update)


cli.add_command(message)

if __name__ == "__main__":
    cli()
