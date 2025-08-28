# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import logging
import shutil
import smtplib
from contextlib import contextmanager
from email import policy
from email.generator import BytesGenerator
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import formataddr, make_msgid, parseaddr
from pathlib import Path

from pyforgejo import PullRequest

from batrachomyomachia.config import pr_patch_files_path, repo_config
from batrachomyomachia.forgejo_api_ops import (
    new_version_pr_comment,
    post_pr_comment,
    update_pr_versions_comment,
)
from batrachomyomachia.local_git_ops import (
    LocalRepoPrInformation,
    PullRequestVersion,
    ensure_local_clone,
    freeze_pr_version,
    msgid_of_cover_letter,
    pr_information_from_local_clone,
    run_git_format_patch,
    update_repo_notes,
)
from batrachomyomachia.templates import (
    pr_cover,
    pr_summary_email_subject,
    pr_summary_email_text,
)
from batrachomyomachia.utilities import (
    PatchPosting,
    PullRequestData,
    deep_get_datetime,
    deep_get_int,
    deep_get_str,
)


@contextmanager
def _smtp_connection(smtp: dict):
    """Establish and return an SMTP connection based on given configuration."""
    server_cls = smtplib.SMTP_SSL if smtp["ssl"] else smtplib.SMTP
    server = server_cls(smtp["host"], smtp["port"])
    server.set_debuglevel(smtp.get("debug", False))

    if smtp.get("tls"):
        server.starttls()
    if smtp.get("user") and smtp.get("password"):
        server.login(smtp["user"], smtp["password"])
    try:
        yield server
    finally:
        server.quit()


def addresses_for_pr_publication(
    pr_data: PullRequestData,
) -> tuple[list[str], list[str]]:
    """Returns the email addresses where a patch should be sent.
    The first element in the tuple is used in the To: header and
    the second in the Cc header."""
    list_name = list_for_pr_publication(pr_data)
    list_address = str(
        repo_config("destination_list_address", pr_data.owner, pr_data.repo)
    )

    return (
        [formataddr((list_name, list_address))],
        pr_data.cc,
    )


def construct_emails_and_headers(
    data: PullRequestData,
    to: list[str],
    cc: list[str],
    patch_files: list[Path],
    local_info: LocalRepoPrInformation,
    current_version: PullRequestVersion,
    previous_version_msgid: str | None,
    repo_html_url: str,
    final_dir: Path,
) -> list[PatchPosting]:
    """Build MIME email objects with appropriate headers for each patch."""
    configured_mail_from = repo_config("mail_from", data.owner, data.repo)
    custom_from_addr = mail_from(data.owner, data.repo, data.pr_data)
    msgid_base = make_msgid(
        domain=parseaddr(custom_from_addr)[1].rsplit("@")[1],
        idstring=f"batrachomyomachia.{data.owner}.{data.repo}.{data.index}.{current_version.version}.IDXIDX",
    )
    cover_msgid = msgid_base.replace("IDXIDX", "0")

    parser = BytesParser(policy=mail_policy())
    postings: list[PatchPosting] = []
    final_dir.mkdir(parents=True)
    for idx, patch_file in enumerate(patch_files):
        with open(patch_file, "rb") as f:
            msg = parser.parse(f)
        patch_msgid = msgid_base.replace("IDXIDX", str(idx))
        from_header = msg.get("From")
        if not from_header:
            msg["From"] = custom_from_addr
        elif from_header == configured_mail_from:
            msg.replace_header("From", custom_from_addr)
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Message-ID"] = patch_msgid
        msg["X-Mailer"] = "batrachomyomachia"
        if data.pr_data.requested_reviewers:
            for requested_reviewer in data.pr_data.requested_reviewers:
                if requested_reviewer.login_name:
                    msg["X-Requested-Reviewer"] = requested_reviewer.login_name
        msg["X-Pull-Request-Organization"] = data.owner
        msg["X-Pull-Request-Repository"] = data.repo
        msg["X-Pull-Request"] = deep_get_str("html_url", data.pr_data)

        if idx == 0 and previous_version_msgid:
            # Send the current patch series version as a reply to the
            # last one.
            msg["References"] = previous_version_msgid
            msg["In-Reply-To"] = previous_version_msgid
        elif idx > 0:
            msg["References"] = cover_msgid
            msg["In-Reply-To"] = cover_msgid
            commit = local_info.commits[idx - 1]
            msg["X-Patch-URL"] = f"{repo_html_url}/commit/{commit.hexsha}"
            postings.append(
                PatchPosting(
                    pull_request_url=deep_get_str("html_url", data.pr_data),
                    version=current_version.version,
                    cover_msgid=cover_msgid,
                    patch_msgid=patch_msgid,
                )
            )

        with open(final_dir / patch_file.name, "wb") as out:
            BytesGenerator(out, policy=mail_policy()).flatten(msg)
    return postings


def generate_cover_letter(
    data: PullRequestData,
    local_info: LocalRepoPrInformation,
    base_ref: str,
    patches_dir: Path,
) -> Path:
    """Generate the patch cover letter file using PR data and templates."""
    cover_txt = patches_dir / "cover.txt"
    body = data.pr_body
    if not body.strip() and len(local_info.commits) == 1:
        messagelines = str(local_info.commits[0].message).strip().splitlines()
        if not messagelines:
            raise ValueError("Empty pr body and empty first message")
        title = messagelines[0]
        try:
            non_empty_index = next(
                i for i, line in enumerate(messagelines[1:]) if line.strip()
            )
        except StopIteration:
            raise ValueError("No non empty line found after the first line")
        body = "\n".join(messagelines[non_empty_index + 1 :]).strip()
    else:
        title = deep_get_str("title", data.pr_data)

    with open(cover_txt, "w") as f:
        f.write(f"{title}\n\n")
        f.write(
            pr_cover(
                listname=list_for_pr_publication(data),
                author=formataddr(
                    (
                        deep_get_str("user.full_name", data.pr_data),
                        deep_get_str("user.email", data.pr_data),
                    )
                ),
                created_at=deep_get_datetime("created_at", data.pr_data),
                updated_at=deep_get_datetime("updated_at", data.pr_data),
                base_repo_full_name=deep_get_str("base.repo.full_name", data.pr_data),
                base_gcc_descr=local_info.base_gcc_descr,
                base_ref=base_ref,
                base_sha=local_info.real_base_sha,
                merge_base=deep_get_str("merge_base", data.pr_data),
                head_repo_full_name=deep_get_str("head.repo.full_name", data.pr_data),
                head_gcc_descr=local_info.head_gcc_desc,
                head_ref=deep_get_str("head.ref", data.pr_data),
                head_sha=local_info.real_head_sha,
                changed_files=deep_get_int("changed_files", data.pr_data),
                additions=deep_get_int("additions", data.pr_data),
                deletions=deep_get_int("deletions", data.pr_data),
                diff=local_info.diff,
                pr_body=body,
                pr_diff_url=deep_get_str("diff_url", data.pr_data),
                pr_html_url=deep_get_str("html_url", data.pr_data),
                requested_reviewers=[
                    r.login for r in data.pr_data.requested_reviewers or [] if r.login
                ],
            )
        )
    return cover_txt


def list_for_pr_publication(pr_data: PullRequestData) -> str:
    """Retrieve the name of the main mailing list where patches are sent."""
    return str(repo_config("destination_list_name", pr_data.owner, pr_data.repo))


def mail_from(owner: str, repo: str, prdata: PullRequest) -> str:
    """Construct a formatted From address for outgoing email based on
    repository settings."""
    name, email = parseaddr(repo_config("mail_from", owner, repo))
    full_name = deep_get_str("user.full_name", prdata)
    return formataddr((f"{full_name} via {name}", email))


def mail_policy():
    """Python's default mail policy wraps headers at 78 characters or so.
    This results in headers getting wrapped and encode-word'ed per RFC 2047.
    (see https://datatracker.ietf.org/doc/html/rfc2047#section-6).
    The problem is that this applies to the In-Reply-To and References headers
    and this breaks threading on clients that expect msgids to be precisely
    those in the Message-Id header.
    This function returns a mail policy that will likely not require wrapping,
    and thus RFC 2047 encoding unless one configures a repository with a very
    long name or uses a very long hostname."""
    return policy.default.clone(max_line_length=300)


def send_patch_emails(data: PullRequestData, patch_files: list[Path], final_dir: Path):
    """Send all patch emails via SMTP."""
    parser = BytesParser(policy=mail_policy())
    with _smtp_connection(repo_config("smtp", data.owner, data.repo)) as smtp:
        for patch_file in patch_files:
            with open(final_dir / patch_file.name, "rb") as f:
                msg = parser.parse(f)
            smtp.send_message(msg)
            logging.info(
                f"Sent message {final_dir / patch_file.name}, {msg['Message-ID']}"
            )


def send_pr_as_patch_series(
    data: PullRequestData, to: list[str], cc: list[str], comment: bool, preview: bool
) -> list[PatchPosting]:
    """This is the main functionality of the /submit and /preview webhook commands
    - The current base and head refs of the branch are stored in a new
      pull request version.
    - A patch series cover is generated based on data from the pull request such as
      the description and additional information calculated from a local copy of the
      upstream repository.
    - git format-patch is invoked to generate a series of patch emails.
    - the emails are augmented with headers that help filter

    Generate and send a series of patch emails for a pull request."""
    repo_url = deep_get_str("base.repo.clone_url", data.pr_data)
    repo_html_url = deep_get_str("head.repo.html_url", data.pr_data)
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
        force=False,
    )
    if not versions:
        raise RuntimeError("No versions found in local repository after freezing PR")

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
            data.client, data.owner, data.repo, data.index, repo_url, versions
        )

    patches_dir = pr_patch_files_path(
        data.owner, data.repo, data.index, versions[-1].version, preview
    )
    shutil.rmtree(patches_dir, ignore_errors=True)
    patches_dir.mkdir(parents=True)

    cover_txt_path = generate_cover_letter(
        data=data, local_info=local_info, base_ref=base_ref, patches_dir=patches_dir
    )

    custom_from_addr = mail_from(data.owner, data.repo, data.pr_data)

    patch_output = run_git_format_patch(
        custom_from_addr, local_repo, patches_dir, cover_txt_path, versions
    )

    patch_files = sorted([f for f in patch_output.iterdir() if f.is_file()])
    if len(patch_files) != len(local_info.commits) + 1:
        raise RuntimeError(
            f"Found {len(patch_files)} for {len(local_info.commits)}"
            " commits plus the cover in {patches_directory}."
        )

    previous_msgid = msgid_of_cover_letter(local_repo, versions)
    final_dir = patches_dir / "final_patches"

    postings = construct_emails_and_headers(
        data=data,
        to=to,
        cc=cc,
        patch_files=patch_files,
        local_info=local_info,
        current_version=versions[-1],
        previous_version_msgid=previous_msgid,
        repo_html_url=repo_html_url,
        final_dir=final_dir,
    )
    if not preview:
        update_repo_notes(
            local_repo, data.owner, data.repo, local_info.commits, postings
        )
    send_patch_emails(data=data, patch_files=patch_files, final_dir=final_dir)
    if comment:
        if postings:
            if preview:
                username = deep_get_str("user.username", data.pr_data)
                sent_to = f"@{username}'s email address"
                msgid = "Message Id of cover message is `<MESSAGEID>`."
            else:
                sent_to = f"{', '.join(to)}"
                msgid = repo_config("link_to_message", data.owner, data.repo)
            if cc:
                sent_to += f" and cc'd {', '.join(cc)}"
            sent = (
                f"Sent patch series version {postings[0].version} "
                + f"containing {len(postings)} patches to {sent_to}.\n"
                + msgid.replace(
                    "MESSAGEID",
                    postings[0].cover_msgid.removeprefix("<").removesuffix(">"),
                )
            )
        else:
            sent = "No patches were sent, sorry."
        post_pr_comment(
            data.client,
            owner=data.owner,
            repo=data.repo,
            pr_index=data.index,
            message=sent,
        )
    return postings


def send_pr_summary_mail(
    toaddr: list[str], prdata: PullRequestData, smtp: dict
) -> None:
    """Send a summary email containing metadata and description of a pull request."""
    message = EmailMessage()
    message["Subject"] = pr_summary_email_subject(prdata.pr_data)
    message["From"] = mail_from(prdata.owner, prdata.repo, prdata.pr_data)
    message["To"] = formataddr(parseaddr(toaddr))
    message["X-Mailer"] = "batrachomyomachia"
    if prdata.pr_data.requested_reviewers:
        for requested_reviewer in prdata.pr_data.requested_reviewers:
            if requested_reviewer.login_name:
                message["X-Requested-Reviewer"] = requested_reviewer.login_name
    message["X-Pull-Request-Organization"] = prdata.owner
    message["X-Pull-Request-Repository"] = prdata.repo
    message["X-Pull-Request"] = deep_get_str("html_url", prdata.pr_data)
    message.set_content(pr_summary_email_text(prdata.pr_data))

    with _smtp_connection(smtp) as server:
        server.send_message(message)
