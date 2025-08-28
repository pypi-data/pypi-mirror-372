# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import hashlib
import hmac
import json
import logging
import re
from email.utils import formataddr, parseaddr

from flask import abort, jsonify, request
from pyforgejo import PyforgejoApi  # type: ignore[import]

from batrachomyomachia.allowlist import (
    allow_user_submit,
    dump_can_submit_list,
    user_can_submit,
)
from batrachomyomachia.config import (
    api_url,
    repo_config,
    repo_is_enabled,
    webhook_celery,
    webhook_secret,
)
from batrachomyomachia.email import (
    addresses_for_pr_publication,
    send_pr_as_patch_series,
)
from batrachomyomachia.forgejo_api_ops import (
    post_pr_comment,
    pr_data_from_url,
    update_pr_welcome_comment,
)
from batrachomyomachia.utilities import RetryException, deep_get_int, deep_get_str

# Regular expressions for matching bot commands
PR_COMMENT_ALLOW_RE = re.compile(r"\s*\/allow\s*", re.MULTILINE | re.IGNORECASE)
PR_COMMENT_PREVIEW_RE = re.compile(r"\s*\/preview\s*", re.MULTILINE | re.IGNORECASE)
PR_COMMENT_SUBMIT_RE = re.compile(r"\s*\/submit\s*", re.MULTILINE | re.IGNORECASE)

encoded_secret = b""


@webhook_celery.task(
    autoretry_for=(RetryException,), retry_backoff=True, queue="incoming"
)
def deal_with(event: str, delivery: str, payload: dict) -> bool:
    """Route webhook event to appropriate handler based on event type and action."""
    if event == "issue_comment":
        action = payload.get("action")
        if action == "created":
            comment_body = payload.get("comment", {}).get("body", "")
            if PR_COMMENT_SUBMIT_RE.fullmatch(comment_body):
                return handle_comment_created_submit(payload)
            elif PR_COMMENT_ALLOW_RE.fullmatch(comment_body):
                return handle_comment_created_allow(payload)
            elif PR_COMMENT_PREVIEW_RE.fullmatch(comment_body):
                return handle_comment_created_preview(payload)
    elif event == "pull_request" and payload.get("action") in {"opened", "reopened"}:
        return handle_pr_opened(payload)
    return False


def handle_comment_created_allow(payload) -> bool:
    """Handle /allow comment by authorizing a user to submit patches."""
    comment_author = deep_get_str("sender.username", payload)
    pr_index = deep_get_int("pull_request.number", payload)
    pr_author = deep_get_str("pull_request.user.username", payload)
    owner = deep_get_str("repository.owner.username", payload)
    repo = deep_get_str("repository.name", payload)
    if not repo_is_enabled(owner, repo):
        logging.info(f"Repository {owner}/{repo} is not enabled")
        return False

    client = PyforgejoApi(
        base_url=api_url(owner, repo), api_key=repo_config("api_key", owner, repo)
    )

    if not user_can_submit(comment_author):
        post_pr_comment(
            client,
            owner,
            repo,
            pr_index,
            f"<!-- pr-allow-error -->Apologies @{comment_author}, "
            "but you are not allowed to perform the /allow action. "
            "Please check the welcome message for instructions.",
        )
        return True

    allow_user_submit(pr_author)
    dump_can_submit_list()
    post_pr_comment(
        client,
        owner,
        repo,
        pr_index,
        f"<!-- pr-allow-success -->Hi @{pr_author}, "
        "you can now perform actions like /allow and /submit.",
    )
    return True


def handle_comment_created_preview(payload) -> bool:
    """Handle /preview comment by sending patch preview to comment author."""
    comment_author = deep_get_str("sender.username", payload)
    owner = deep_get_str("repository.owner.username", payload)
    repo = deep_get_str("repository.name", payload)
    if not repo_is_enabled(owner, repo):
        logging.info(f"Repository {owner}/{repo} is not enabled")
        return False

    client = PyforgejoApi(
        base_url=api_url(owner, repo), api_key=repo_config("api_key", owner, repo)
    )

    pr_index = deep_get_int("pull_request.number", payload)
    if not user_can_submit(comment_author):
        post_pr_comment(
            client,
            owner,
            repo,
            pr_index,
            f"<!-- pr-allow-error -->Apologies @{comment_author}, but you are not "
            "allowed to perform the /preview action. Please check the welcome "
            "message for instructions.",
        )
        return True

    pr_url = deep_get_str("pull_request.url", payload)
    # We use the pull_request.user dict rather than the sender,
    # because sender contains an invalid email address
    to = [
        formataddr(
            (
                deep_get_str("pull_request.user.full_name", payload),
                deep_get_str("pull_request.user.email", payload),
            )
        )
    ]

    data = pr_data_from_url(pr_url)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr_url}")
    if parseaddr(to[0]) == ("", ""):
        post_pr_comment(
            data.client,
            data.owner,
            data.repo,
            data.index,
            f"<!-- pr-not-posted -->Cannot post as `{to[0]}`"
            + " is not a valid email address.",
        )
        return True

    send_pr_as_patch_series(data=data, to=to, cc=[], comment=True, preview=True)
    return True


def handle_comment_created_submit(payload) -> bool:
    """Handle /submit comment by sending patch to mailing list."""
    owner = deep_get_str("repository.owner.username", payload)
    repo = deep_get_str("repository.name", payload)
    if not repo_is_enabled(owner, repo):
        logging.info(f"Repository {owner}/{repo} is not enabled")
        return False

    comment_author = deep_get_str("sender.username", payload)
    client = PyforgejoApi(
        base_url=api_url(owner, repo), api_key=repo_config("api_key", owner, repo)
    )

    pr_index = deep_get_int("pull_request.number", payload)
    if not user_can_submit(comment_author):
        post_pr_comment(
            client,
            owner,
            repo,
            pr_index,
            f"<!-- pr-allow-error -->Apologies @{comment_author}, "
            "but you are not allowed to perform the /submit action. "
            "Please check the welcome message for instructions.",
        )
        return True

    pr_author = deep_get_str("pull_request.user.username", payload)
    if pr_author != comment_author:
        post_pr_comment(
            client,
            owner,
            repo,
            pr_index,
            f"<!-- pr-allow-error -->Apologies @{comment_author}, "
            f"but only the pull request author @{pr_author} may perform /submit.",
        )
        return True

    pr_url = deep_get_str("pull_request.url", payload)
    data = pr_data_from_url(pr_url)
    if not data:
        raise RuntimeError(f"Could not retrieve data from {pr_url}")

    to, cc = addresses_for_pr_publication(data)
    errors = ""
    for email in to + cc:
        if parseaddr(email) == ("", ""):
            errors += f"- {email} is not a valid email address"
    if errors:
        post_pr_comment(
            data.client,
            data.owner,
            data.repo,
            data.index,
            f"<!-- pr-not-posted -->Cannot post as:\n{errors}",
        )
        return True

    send_pr_as_patch_series(data=data, to=to, cc=cc, comment=True, preview=False)
    return True


def handle_pr_opened(payload) -> bool:
    """Post a welcome message to new or reopened pull requests."""
    pr_index = deep_get_int("pull_request.number", payload)
    username = deep_get_str("pull_request.user.username", payload)
    owner = deep_get_str("repository.owner.username", payload)
    repo = deep_get_str("repository.name", payload)
    if not repo_is_enabled(owner, repo):
        logging.info(f"Repository {owner}/{repo} is not enabled")
        return False

    client = PyforgejoApi(
        base_url=api_url(owner, repo), api_key=repo_config("api_key", owner, repo)
    )

    update_pr_welcome_comment(
        client=client,
        owner=owner,
        repo=repo,
        pr_index=pr_index,
        sitename=repo_config("site_name", owner, repo),
        username=username,
        site_help_resources=repo_config("site_help_resources", owner, repo, ""),
        repository_help_resources=repo_config("help_resources", owner, repo, ""),
        repository_patch_guidelines=repo_config("patch_guidelines", owner, repo, ""),
    )
    return True


def setup_encoded_secret():
    """Load and encode the webhook secret for validating requests."""
    global encoded_secret
    encoded_secret = webhook_secret().encode()
    return True


def webhook_receiver():
    """HTTP endpoint to handle incoming webhook events from Forgejo."""
    signature_hash = request.headers.get("X-Forgejo-Signature")
    if not signature_hash:
        logging.warning("Missing signature header")
        abort(403)

    mac = hmac.new(encoded_secret, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature_hash):
        logging.warning("Signature mismatch")
        abort(403)

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    event = (
        request.headers.get("X-Forgejo-Event")
        or request.headers.get("X-Gitea-Event")
        or request.headers.get("X-GitHub-Event")
    )
    if not event:
        return jsonify({"error": "Missing event"}), 400

    delivery = (
        request.headers.get("X-Forgejo-Delivery")
        or request.headers.get("X-Gitea-Delivery")
        or request.headers.get("X-GitHub-Delivery")
    )
    if not delivery:
        return jsonify({"error": "Missing delivery ID"}), 400

    payload = request.get_json()
    logging.info(
        json.dumps(
            {"event": event, "delivery": delivery, "payload": payload},
            separators=(",", ":"),
            default=str,
        )
    )
    deal_with.delay(event, delivery, payload)
    return jsonify({"status": "queued"}), 202
