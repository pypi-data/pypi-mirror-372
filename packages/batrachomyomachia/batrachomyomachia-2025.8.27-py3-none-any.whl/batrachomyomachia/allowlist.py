# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import logging

from filelock import FileLock
from ruamel.yaml import YAML

from batrachomyomachia.config import allowed_users_path, redis_service
from batrachomyomachia.utilities import dump

REDIS_KEY = "allow_user_submit"


def allow_user_submit(username: str) -> None:
    """
    Add a username to the Redis set that permits webhook command execution.
    """
    if not username:
        logging.error("Username is empty")
        return
    redis = redis_service()
    redis.sadd(REDIS_KEY, username)


def dump_can_submit_list() -> None:
    """
    Serialize the Redis set of allowed usernames to a YAML file.
    """
    redis = redis_service()
    members = sorted(
        [user.decode("utf-8") for user in redis.smembers(REDIS_KEY)]  # type: ignore
    )
    output_path = allowed_users_path()
    lock_path = output_path.with_name(f"{output_path.name}.lock")
    with FileLock(lock_path):
        with open(output_path, "w") as f:
            dump(members, f)


def user_can_submit(username: str) -> bool:
    """Check if a user is allowed to perform commands via the webhook."""
    redis = redis_service()
    return bool(redis.sismember(REDIS_KEY, username))


def update_redis_list() -> None:
    """
    Synchronize the Redis allowlist with the contents of the YAML file.
    """
    redis = redis_service()
    current_members = {
        user.decode("utf-8")
        for user in redis.smembers(REDIS_KEY)  # type: ignore
    }
    yaml_path = allowed_users_path()
    lock_path = yaml_path.with_suffix(".lock")
    with FileLock(lock_path):
        if not yaml_path.exists():
            logging.error(f"{yaml_path} does not exist.")
            return
        with open(yaml_path) as f:
            file_contents = f.read().strip()
    yaml = YAML(typ="safe", pure=True)
    desired_members = set(yaml.load(file_contents) or [])

    # Remove users not in the YAML file
    redis.srem(REDIS_KEY, *(current_members - desired_members))

    # Add new users from YAML file
    redis.sadd(REDIS_KEY, *(desired_members - current_members))
