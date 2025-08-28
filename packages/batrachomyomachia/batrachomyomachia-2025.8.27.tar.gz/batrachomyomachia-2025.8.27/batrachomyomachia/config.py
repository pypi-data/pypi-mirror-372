# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import importlib.resources
from functools import cache
from pathlib import Path
from typing import Any

import platformdirs
import redis
from celery import Celery  # type: ignore[import]
from dynaconf import Dynaconf  # type: ignore[import]
from kombu import Queue  # type: ignore[import]

with importlib.resources.path("batrachomyomachia", "default-settings.yml") as default:
    settings_files = [
        str(default),
        str(platformdirs.site_config_path("batrachomyomachia") / "settings.yml"),
        str(platformdirs.user_config_path("batrachomyomachia") / "settings.yml"),
        "settings.yml",
        ".secrets.yml",
    ]
    settings = Dynaconf(
        envvar_prefix="BMM",
        settings_files=settings_files,
    )

webhook_celery = Celery("batrachomyomachia", broker=settings["webhook_task_broker_url"])
webhook_celery.conf.task_queues = (
    Queue("default"),
    Queue("incoming"),
    Queue("maintenance"),
)


def repo_config(key: str, owner: str, reponame: str, default: Any = None) -> Any:
    """Return a configuration value that can be overridden on a per-repository basis."""
    match: dict = next(
        (
            repo
            for repo in settings["repositories"]
            if repo["owner"] == owner and repo["name"] == reponame
        ),
        {},
    )
    return match.get(key, settings.get(key, default=default))


def allowed_users_path() -> Path:
    """Return path to the allowed users YAML file."""
    path = settings["allowed_users_path"]
    if path:
        return Path(path)
    return (
        Path(platformdirs.user_cache_dir("batrachomyomachia", ensure_exists=True))
        / "allowed_users.yaml"
    )


def api_url(owner: str, reponame: str) -> str:
    """Construct API base URL from repository configuration."""
    forgejo_url = repo_config("forgejo_url", owner, reponame)
    if not forgejo_url:
        raise RuntimeError("Please configure: forgejo_url")
    return forgejo_url.rstrip("/") + "/api/v1"


def custom_template_path() -> Path:
    """Return path where site-specific templates can be found."""
    return Path(settings["custom_template_path"])


def flower_address() -> str:
    """Return the address where the Celery Flower service listens on."""
    address = settings["flower_address"]
    if not address:
        raise RuntimeError("Please configure: flower_address")
    return address


def flower_port() -> int:
    """Return the port number where the Celery Flower service listens on."""
    port = settings["flower_port"]
    if not port:
        raise RuntimeError("Please configure: flower_port")
    try:
        return int(port)  # type: ignore
    except ValueError as e:
        raise ValueError(f"Invalid flower_port value: {port}") from e


def local_git_repo_path(owner: str, repo: str) -> Path:
    """Return the location on disk where mirror repositories are kept."""
    root = repo_config("local_git_repos", owner, repo)
    if not root:
        root = platformdirs.user_cache_dir("batrachomyomachia", ensure_exists=True)
    return Path(root) / "mirrors" / owner / repo


def loglevel() -> str:
    """Return the global log level."""
    level = settings["loglevel"]
    if not level:
        raise RuntimeError("Please configure: loglevel")
    return level


def pr_patch_files_path(
    owner: str, repo: str, pr_index: int, patch_version: int, preview: bool
) -> Path:
    """Return the location on disk where patch files are archived."""
    base = repo_config("pr_patch_files_path", owner, repo)
    if not base:
        base = platformdirs.user_cache_dir("batrachomyomachia", ensure_exists=True)
    return (
        Path(base)
        / ("preview_patch_files" if preview else "pr_patch_files")
        / owner
        / repo
        / str(pr_index)
        / str(patch_version)
    )


def redis_service() -> redis.Redis:
    """Return a redis connection object."""
    return redis.from_url(settings["webhook_task_broker_url"])


def repo_is_enabled(owner: str, name: str) -> bool:
    return f"{owner}/{name}" in repositories()


@cache
def repositories() -> set[str]:
    return set([f"{repo.owner}/{repo.name}" for repo in settings["repositories"]])


def webhook_address() -> str:
    """Return the address where the webhook listens on."""
    address = settings["webhook_address"]
    if not address:
        raise RuntimeError("Please configure: webhook_address")
    return address


def webhook_port() -> int:
    """Return the port number where the webhook listens on."""
    port = settings["webhook_port"]
    if not port:
        raise RuntimeError("Please configure: webhook_port")
    try:
        return int(port)  # type: ignore
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid webhook_port value: {port}") from e


def webhook_secret() -> str:
    """Return the secret value shared between forgejo and the webhook."""
    secret = settings["webhook_secret"]
    if not secret:
        raise RuntimeError("Please configure: webhook_secret")
    return secret


def webhook_worker_concurrency() -> int:
    concurrency = settings["webhook_worker_concurrency"]
    if not concurrency:
        raise RuntimeError("Please configure: webhook_worker_concurrency")
    try:
        return int(concurrency)  # type: ignore
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid concurrency value: {concurrency}") from e
