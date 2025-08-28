# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import logging
from urllib.parse import urlparse

from pyforgejo import PyforgejoApi  # type: ignore[import]

from batrachomyomachia.config import api_url, repo_config
from batrachomyomachia.templates import (
    pr_new_version,
    pr_versions_text,
    pr_welcome_text,
)
from batrachomyomachia.utilities import (
    LocalRepoPrInformation,
    PullRequestData,
    PullRequestVersion,
    deep_get_str,
    read_pr_body,
)


def extract_pr_components(pr_url: str) -> tuple[str, str, int] | None:
    """Extract the (owner, repo, PR index) components from a PR URL."""
    pr_parsed = urlparse(pr_url)
    pr_path = pr_parsed.path.strip("/").split("/")
    if len(pr_path) < 4 or pr_path[-2] != "pulls":
        logging.error(
            f"PR url {pr_url} must be in the form forge-server/org/repo/pulls/number"
        )
        return None
    try:
        return (pr_path[-4], pr_path[-3], int(pr_path[-1]))
    except ValueError:
        logging.error(
            f"PR url {pr_url} must be in the form"
            f" forge-server/org/repo/pulls/number. Last element {pr_path[-1]}"
        )
        return None


def new_version_pr_comment(
    client: PyforgejoApi,
    owner: str,
    repo: str,
    pr_index: int,
    version_number: int,
    local_info: LocalRepoPrInformation,
):
    message = pr_new_version(version_number=version_number, commits=local_info.commits)
    post_pr_comment(client, owner, repo, pr_index, message)


def post_or_replace_pr_comment(
    client: PyforgejoApi,
    owner: str,
    repo: str,
    pr_index: int,
    message: str,
    replace_header: str,
    in_place: bool,
):
    """Replace a comment by the current user that starts with a specific string."""
    if not replace_header:
        # Do not delete all comments!
        raise RuntimeError(
            "post_or_replace_pr_comment called with empty replace_header"
        )
    logging.info(f"Posting comment in {pr_index}")
    comments = client.issue.get_comments(owner=owner, repo=repo, index=pr_index)
    found_ids: list[int] = []
    for comment in comments:
        if (
            comment.user
            and comment.user.login
            and comment.user.login == repo_config("forge_username", owner, repo)
            and comment.body
            and comment.body.strip().startswith(replace_header.strip())
        ):
            if not comment.id:
                raise RuntimeError("comment with null id")
            found_ids.append(comment.id)
    if in_place and found_ids:
        if len(found_ids) > 1:
            for id in found_ids[0:-1]:
                client.issue.delete_comment(owner=owner, repo=repo, id=id)
        client.issue.edit_comment(
            owner=owner, repo=repo, id=found_ids[-1], body=message
        )
    else:
        for id in found_ids:
            client.issue.delete_comment(owner=owner, repo=repo, id=id)
        client.issue.create_comment(
            owner=owner, repo=repo, index=pr_index, body=message
        )


def post_pr_comment(
    client: PyforgejoApi, owner: str, repo: str, pr_index: int, message: str
):
    """Post a comment to a pull request review using the Forgejo API."""
    logging.info(f"Posting comment in {pr_index}")
    client.issue.create_comment(owner=owner, repo=repo, index=pr_index, body=message)


def pr_data_from_url(pr_url: str) -> PullRequestData | None:
    """Fetch pull request data from a Forgejo PR URL."""
    components = extract_pr_components(pr_url)
    if not components:
        return None
    (owner, repo, pr_index) = components

    client = PyforgejoApi(
        base_url=api_url(owner, repo), api_key=repo_config("api_key", owner, repo)
    )
    pr_data = client.repository.repo_get_pull_request(
        owner=owner,
        repo=repo,
        index=pr_index,
    )
    body, cc = read_pr_body(deep_get_str("body", pr_data))
    return PullRequestData(
        url=pr_url,
        owner=owner,
        repo=repo,
        index=pr_index,
        client=client,
        pr_data=pr_data,
        pr_body=body,
        cc=cc,
    )


def update_pr_versions_comment(
    client: PyforgejoApi,
    owner: str,
    repo: str,
    pr_index: int,
    repo_url: str,
    versions: list[PullRequestVersion],
):
    """Post or update the PR comment listing available patch versions."""
    body = pr_versions_text(repo_url, pr_index, versions)
    post_or_replace_pr_comment(
        client, owner, repo, pr_index, body, "<!-- pr-versions -->", False
    )


def update_pr_welcome_comment(
    client: PyforgejoApi,
    owner: str,
    repo: str,
    pr_index: int,
    sitename: str,
    username: str,
    site_help_resources: str,
    repository_help_resources: str,
    repository_patch_guidelines: str,
):
    """Post or update the welcome comment on a pull request with helpful resources."""
    body = pr_welcome_text(
        sitename=sitename,
        username=username,
        site_help_resources=site_help_resources,
        repository_help_resources=repository_help_resources,
        repository_patch_guidelines=repository_patch_guidelines,
    )
    post_or_replace_pr_comment(
        client, owner, repo, pr_index, body, "<!-- pr-welcome -->", True
    )
