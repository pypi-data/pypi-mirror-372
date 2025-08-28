# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import importlib.metadata
import logging
from email.utils import formataddr

import click
from asgiref.wsgi import WsgiToAsgi
from flask import Flask
from pyforgejo import PyforgejoApi  # type: ignore[import]

from batrachomyomachia.allowlist import allow_user_submit, dump_can_submit_list
from batrachomyomachia.config import (
    api_url,
    flower_address,
    flower_port,
    loglevel,
    repo_config,
    settings,
    webhook_address,
    webhook_celery,
    webhook_port,
    webhook_worker_concurrency,
)
from batrachomyomachia.cron import discover_cron_jobs
from batrachomyomachia.email import send_pr_as_patch_series, send_pr_summary_mail
from batrachomyomachia.forgejo_api_ops import (
    extract_pr_components,
    new_version_pr_comment,
    pr_data_from_url,
    update_pr_versions_comment,
    update_pr_welcome_comment,
)
from batrachomyomachia.local_git_ops import (
    ensure_local_clone,
    freeze_pr_version,
    pr_information_from_local_clone,
)
from batrachomyomachia.utilities import deep_get_str
from batrachomyomachia.webhook import webhook_receiver

VERSION = importlib.metadata.version("batrachomyomachia")


@click.group()
def cli():
    """Configure logging for all commands."""
    logging.basicConfig(
        level=logging.getLevelNamesMapping()[settings["loglevel"].upper()],
        format=settings["log_format"],
    )


@click.command(help="Allow a user to run webhook commands such as /allow and /submit")
@click.option(
    "--username", required=True, help="Username allowed to run commands via the webhook"
)
def allow(username):
    logging.info(f"Allowing user {username} to run webhook commands.")
    allow_user_submit(username)
    dump_can_submit_list()


@click.command(help="Launch the Celery Flower monitoring UI.")
@click.option("--host", default=flower_address(), help="Host address to listen on")
@click.option("--port", default=flower_port(), type=int, help="Port to listen on")
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
def flower(host, port, debug):
    logging.info("Starting flower.")
    webhook_celery.autodiscover_tasks(["batrachomyomachia.webhook"])
    args = ["flower", f"--address={host}", f"--port={port}"]
    if debug:
        args.append("--debug")
    webhook_celery.start(args)


@click.command(help="Freeze a pull request into a new version.")
@click.option("--pr", required=True, help="Pull request URL")
@click.option("--force", is_flag=True, help="Force creation of new version.")
def freeze(pr, force):
    logging.info(f"Freezing the current version of {pr}.")
    data = pr_data_from_url(pr)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr}.")

    repo_url = deep_get_str("base.repo.clone_url", data.pr_data)
    head_sha = deep_get_str("head.sha", data.pr_data)
    base_ref = deep_get_str("base.ref", data.pr_data)

    local_repo = ensure_local_clone(data.owner, data.repo)

    new_version, versions = freeze_pr_version(
        repo=local_repo,
        owner=data.owner,
        reponame=data.repo,
        pr_index=data.index,
        head_sha=head_sha,
        base_ref=base_ref,
        force=force,
    )

    if not versions:
        raise RuntimeError(
            "No versions could be read from repository after freezing PR"
        )

    local_info = pr_information_from_local_clone(
        local_repo=local_repo,
        head_sha=head_sha,
        base_ref=base_ref,
        owner=data.owner,
        repo=data.repo,
    )

    if new_version:
        new_version_pr_comment(
            data.client,
            data.owner,
            data.repo,
            data.index,
            versions[-1].version,
            local_info,
        )
        update_pr_versions_comment(
            data.client,
            data.owner,
            data.repo,
            data.index,
            repo_url,
            versions,
        )


@click.command(help="Email the patch preview of a pull request to the author.")
@click.option("--pr", required=True, help="Pull request URL")
def preview(pr):
    logging.info(f"Sending patch preview of {pr} to author")
    data = pr_data_from_url(pr)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr}")

    recipient = [
        formataddr(
            (
                deep_get_str("user.full_name", data.pr_data),
                deep_get_str("user.email", data.pr_data),
            )
        )
    ]
    send_pr_as_patch_series(data=data, to=recipient, cc=[], comment=False, preview=True)


@click.command(help="Send a pull request patch review to the specified recipients.")
@click.option("--pr", required=True, help="Pull request URL")
@click.option("--to", required=True, multiple=True, help="Email recipients")
@click.option("--cc", multiple=True, help="cc Email recipients")
def submit(pr, to, cc):
    """Send a pull request patch to the specified recipients."""
    logging.info(f"Submitting patch of {pr} to {to}")
    data = pr_data_from_url(pr)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr}")
    send_pr_as_patch_series(data=data, to=to, cc=cc, comment=False, preview=False)


@click.command(help="Send a summary email of the pull request.")
@click.option("--pr", required=True, help="Pull request URL")
@click.option("--to", required=True, multiple=True, help="Email recipients")
def summary(pr, to):
    logging.info(f"Sending summary of {pr} to {to}")
    data = pr_data_from_url(pr)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr}")
    smtp = repo_config("smtp", data.owner, data.repo)
    send_pr_summary_mail(to, data, smtp)


@click.command(help="Start the webhook server using Flask or Uvicorn.")
@click.option(
    "--host", default=webhook_address(), help="Webhook server host address to listen on"
)
@click.option(
    "--port", default=webhook_port(), type=int, help="Webhook server port to listen on"
)
@click.option("--uvicorn", is_flag=True, help="Use Uvicorn ASGI server")
@click.option("--debug", is_flag=True, help="Enable debug and auto-reload")
def webhook(host, port, uvicorn, debug):
    """Start the webhook server using Flask or Uvicorn."""
    logging.info(f"Starting batrachomyomachia webhook version {VERSION}")
    if debug:
        import os

        from dynaconf.utils.inspect import get_debug_info  # type: ignore[import]

        logging.info(f"Started in {os.getcwd()}")
        logging.info(f"configuration loading: {get_debug_info(settings)}")
    from batrachomyomachia.webhook import setup_encoded_secret

    if not setup_encoded_secret():
        return 1

    app = Flask(__name__)
    app.add_url_rule("/webhook", view_func=webhook_receiver, methods=["POST"])

    if uvicorn:
        import uvicorn as u

        u.run(
            WsgiToAsgi(app),
            host=host,
            port=port,
            reload=debug,
            timeout_graceful_shutdown=10,
            lifespan="off",
        )
    else:
        logging.warning("Do not use this in production!")
        app.run(debug=debug, host=host, port=int(port))


@click.command(help="Send a welcome comment to the pull request author.")
@click.option("--pr", required=True, help="Pull request URL")
def welcome(pr):
    """Send a welcome comment to the pull request author."""
    logging.info(f"Sending a welcome comment to {pr}")
    components = extract_pr_components(pr)
    if not components:
        return

    owner, repo, pr_index = components
    client = PyforgejoApi(
        base_url=api_url(owner, repo),
        api_key=repo_config("api_key", owner, repo),
    )

    pr_data = client.repository.repo_get_pull_request(
        owner=owner, repo=repo, index=pr_index
    )
    username = deep_get_str("user.username", pr_data)

    update_pr_welcome_comment(
        client,
        owner,
        repo,
        pr_index,
        repo_config("site_name", owner, repo),
        username,
        repo_config("site_help_resources", owner, repo, ""),
        repo_config("help_resources", owner, repo, ""),
        repo_config("patch_guidelines", owner, repo, ""),
    )


@click.command(help="Start Celery worker for webhook message handling.")
@click.option(
    "--concurrency", default=webhook_worker_concurrency(), help="Parallel workers"
)
@click.option("--loglevel", default=loglevel(), help="Logging level")
@click.option(
    "--solo", is_flag=True, default=False, help="Run worker in solo mode for debugging"
)
@click.option("--skip-cron", is_flag=True, default=False, help="Do not start cron jobs")
def worker(concurrency, loglevel, solo, skip_cron):
    """Start Celery worker for webhook message handling."""
    logging.info(
        f"Starting batrachomyomachia webhook message handlers version {VERSION}"
    )
    webhook_celery.autodiscover_tasks(
        ["batrachomyomachia.cron", "batrachomyomachia.webhook"]
    )
    discover_cron_jobs()
    args = ["worker", f"--loglevel={loglevel}"]
    if not skip_cron:
        args.append("-B")
    args.append("--pool=solo" if solo else f"--concurrency={concurrency}")
    webhook_celery.worker_main(args)


# Register all commands to the CLI group
cli.add_command(allow)
cli.add_command(flower)
cli.add_command(freeze)
cli.add_command(preview)
cli.add_command(submit)
cli.add_command(summary)
cli.add_command(webhook)
cli.add_command(welcome)
cli.add_command(worker)

if __name__ == "__main__":
    cli()
