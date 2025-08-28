# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.
import logging

from celery.schedules import crontab # type: ignore[import]

from batrachomyomachia.config import (
    repo_config,
    repo_is_enabled,
    settings,
    webhook_celery,
)
from batrachomyomachia.local_git_ops import (
    ensure_local_clone,
    update_repo_branches,
)
from batrachomyomachia.utilities import RetryException


def discover_cron_jobs():
    """Configure the Celery Beat scheduler based on repository configuration"""
    schedule = {}
    for repo in settings["repositories"]:
        mirror_refs_mappings = repo_config(
            "mirror_refs_mappings", repo.owner, repo.name
        )
        mirror_schedule = repo_config("mirror_schedule", repo.owner, repo.name)
        if isinstance(mirror_schedule, dict):
            c = crontab(**mirror_schedule)
        elif isinstance(mirror_schedule, str):
            c = crontab.from_string(mirror_schedule)
        elif isinstance(mirror_schedule, (int, float)):
            c = mirror_schedule
        else:
            continue
        schedule[f"mirror-of-{repo.owner}-{repo.name}"] = {
            "task": "batrachomyomachia.cron.sync_repository_refs",
            "schedule": c,
            "args": (repo.owner, repo.name, mirror_refs_mappings),
        }
    webhook_celery.conf.beat_schedule = schedule


@webhook_celery.task(
    autoretry_for=(RetryException,), retry_backoff=True, queue="maintenance"
)
def sync_repository_refs(owner: str, repo: str, refs_mappings: list[str]) -> bool:
    """Sync specific refs from the upstream repository to the origin.
    This code is used in situations where the forgejo repository is not the
    "official" mirror. Upstream in this case is the official mirror and origin
    is the repository in forgejo.
    """
    if not repo_is_enabled(owner, repo):
        logging.info(f"Repository {owner}/{repo} is not enabled")
        return False
    local_repo = ensure_local_clone(owner, repo)
    update_repo_branches(local_repo, owner, repo, refs_mappings)

    return True
