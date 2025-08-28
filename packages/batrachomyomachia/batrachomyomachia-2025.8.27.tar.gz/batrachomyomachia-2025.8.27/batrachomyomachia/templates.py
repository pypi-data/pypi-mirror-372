# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

from datetime import datetime

from git import Commit, Diff, DiffIndex
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, Template
from pyforgejo import PullRequest

from batrachomyomachia.config import custom_template_path
from batrachomyomachia.utilities import PullRequestVersion


def template_loader() -> ChoiceLoader:
    """Create a Jinja2 template loader supporting both user and package templates."""
    user_template_path = custom_template_path()
    return ChoiceLoader(
        [
            FileSystemLoader(user_template_path),
            PackageLoader("batrachomyomachia", "templates"),
        ]
    )


def template_environment() -> Environment:
    """Initialize and return a Jinja2 environment using the custom loader."""
    return Environment(loader=template_loader())


def get_template(template_name: str) -> Template:
    """Load and return a named Jinja2 template."""
    return template_environment().get_template(template_name)


def pr_cover(
    listname: str,
    author: str,
    created_at: datetime,
    updated_at: datetime,
    base_repo_full_name: str,
    base_gcc_descr: str | None,
    base_ref: str,
    base_sha: str,
    merge_base: str,
    head_repo_full_name: str,
    head_gcc_descr: str | None,
    head_ref: str,
    head_sha: str,
    changed_files: int,
    additions: int,
    deletions: int,
    diff: DiffIndex[Diff],
    pr_body: str,
    pr_diff_url: str,
    pr_html_url: str,
    requested_reviewers: list[str],
) -> str:
    """Render the patch series cover letter."""
    template = get_template("pr-cover.j2")
    return template.render(
        {
            "listname": listname,
            "author": author,
            "created_at": created_at,
            "updated_at": updated_at,
            "changed_files": changed_files,
            "additions": additions,
            "deletions": deletions,
            "base_repo_full_name": base_repo_full_name,
            "head_repo_full_name": head_repo_full_name,
            "head_ref": head_ref,
            "head_sha": head_sha,
            "base_ref": base_ref,
            "base_sha": base_sha,
            "head_gcc_descr": head_gcc_descr,
            "base_gcc_descr": base_gcc_descr,
            "merge_base": merge_base,
            "pr_diff_url": pr_diff_url,
            "pr_html_url": pr_html_url,
            "requested_reviewers": requested_reviewers,
            "pr_body": pr_body,
            "diff": diff,
        }
    )


def pr_new_version(version_number: int, commits: list[Commit]) -> str:
    """Render the PR comment showing available patch series versions."""
    template = get_template("pr-new-version.j2")
    return template.render(
        {
            "version_number": version_number,
            "commits": commits,
        }
    )


def pr_summary_email_subject(data: PullRequest) -> str:
    """Generate a short email subject line summarizing the PR."""
    template = Template("[{{ base.repo.full_name }}] #{{ number }} {{ title }}")
    return template.render(data.dict())


def pr_summary_email_text(data: PullRequest) -> str:
    """Render the text body for a summary email of the pull request."""
    template = get_template("pr-summary-email-text.j2")
    return template.render(data.dict())


def pr_versions_text(
    repo_url: str, pr_index: int, versions: list[PullRequestVersion]
) -> str:
    """Render the PR comment showing available patch series versions."""
    template = get_template("pr-versions.j2")
    return template.render(
        {
            "repo_url": repo_url,
            "pr_index": pr_index,
            "versions": versions,
        }
    )


def pr_welcome_text(
    sitename: str,
    username: str,
    site_help_resources: str,
    repository_help_resources: str,
    repository_patch_guidelines: str,
) -> str:
    """Render the welcome message for a new pull request with guidance links."""
    template = get_template("pr-welcome.j2")
    return template.render(
        {
            "sitename": sitename,
            "username": username,
            "site_help_resources": site_help_resources,
            "repository_help_resources": repository_help_resources,
            "repository_patch_guidelines": repository_patch_guidelines,
        }
    )
