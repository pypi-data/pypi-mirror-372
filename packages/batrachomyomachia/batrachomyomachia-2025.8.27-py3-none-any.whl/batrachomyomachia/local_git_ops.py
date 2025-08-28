# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Arm Ltd.

import logging
import re
import shlex
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import asdict
from enum import Enum
from pathlib import Path

import git
import redis
import redis.lock  # type: ignore[import]
from git.exc import BadName, GitCommandError
from ruamel.yaml import YAML

from batrachomyomachia.config import local_git_repo_path, redis_service, repo_config
from batrachomyomachia.forgejo_api_ops import PullRequestVersion
from batrachomyomachia.utilities import (
    LocalRepoPrInformation,
    PatchPosting,
    RetryException,
)

REPO_LOCK_TIMEOUT = 120
VERSIONED_PULL_PREFIX = "refs/versioned_pull"

BASEPOINT_WITH_PATCH_RE = re.compile(r"^basepoints/gcc-(\d+)-(\d+)-g[0-9a-f]*$")
BASEPOINT_WITHOUT_PATCH_RE = re.compile(r"^basepoints/gcc-(\d+)$")
RELEASE_NUM_RE = re.compile(r"r\d+$")
RELEASE_REF_RE = re.compile(r"^r(\d+)-\d+(-g[0-9a-f]+)?$")
VERSIONED_PULL_REF_RE = re.compile(r"refs/versioned_pull/(\d+)/(\d+)/(base|head)")


class GccGitDescrWays(Enum):
    """Mode of operation for the gcc descr algorithm."""

    VANILLA = 1
    SHORT = 2
    LONG = 3


def ensure_local_clone(owner: str, reponame: str) -> git.Repo:
    """
    Clone or reuse a bare repo, adding an upstream if configured.
    """
    path = Path(local_git_repo_path(owner, reponame))
    path.parent.mkdir(parents=True, exist_ok=True)

    ssh_url = repo_config("origin_url", owner, reponame)
    upstream_url = repo_config("upstream_url", owner, reponame)
    with local_repo_lock(owner, reponame):
        if not path.exists():
            logging.info(f"{owner}/{reponame} clone: Cloning {ssh_url} -> {path}")
            repo = git.Repo.clone_from(
                ssh_url, path, env=git_env(owner, reponame), bare=True
            )
        else:
            logging.debug(f"{owner}/{reponame} clone: Using {ssh_url} clone in {path}")
            repo = git.Repo(path)
        repo.git.update_environment(**git_env(owner, reponame))
        origin = repo.remote("origin")
        if upstream_url:
            if "upstream" not in repo.remotes:
                logging.info(
                    f"{owner}/{reponame} clone: Creating remote upstream {upstream_url}"
                )
                upstream = repo.create_remote("upstream", upstream_url)
            else:
                upstream = repo.remote("upstream")
        else:
            upstream = None

        if upstream:
            logging.info(
                f"{owner}/{reponame} clone: Fetching refs from upstream {upstream_url}"
            )
            # upstream repository beats everything
            upstream.fetch(refspec="refs/*:refs/*", force=True)
            # Except our notes, pull requests and versioned pull requests
            logging.info(
                f"{owner}/{reponame} clone: Fetching notes, PRs and versioned PRs"
                f" from origin {ssh_url}"
            )
            origin.fetch(
                refspec="refs/notes/batrachomyomachia/*:refs/notes/batrachomyomachia/*",
                force=True,
            )
            origin.fetch(refspec="refs/pull/*:refs/pull/*", force=True)
            origin.fetch(
                refspec=f"{VERSIONED_PULL_PREFIX}/*:{VERSIONED_PULL_PREFIX}/*",
                force=True,
            )
        else:
            logging.info(
                f"{owner}/{reponame} clone: Fetching refs from origin {ssh_url}"
            )
            origin.fetch(refspec="refs/*:refs/*", force=True)
        return repo


def freeze_pr_version(
    repo: git.Repo,
    owner: str,
    reponame: str,
    pr_index: int,
    head_sha: str,
    base_ref: str,
    force: bool,
) -> tuple[bool, list[PullRequestVersion]]:
    # Fetch updates
    with local_repo_lock(owner, reponame):
        versions = read_pull_versions(repo, pr_index)
        head = repo.commit(head_sha)
        # The base.sha in the PR data points at the original sha when the PR was created
        # If the developer has force pushed changes, we must recalculate the merge base
        # ourselves
        base_sha = repo.git.merge_base(f"refs/heads/{base_ref}", head)
        base = repo.commit(base_sha)

        if versions:
            last = versions[-1]
            if (
                not force
                and last.head_ref == head.hexsha
                and last.base_ref == base.hexsha
            ):
                logging.info(
                    f"{owner}/{reponame} freeze: The current base and head refs have"
                    f" already been recorded as version {last.version}"
                )
                return False, versions
            v_num = last.version + 1
        else:
            v_num = 1

        write_versioned_pull_refs(repo, pr_index, v_num, head, base)
        repo.remote("origin").push(
            f"{VERSIONED_PULL_PREFIX}/{pr_index}/*:{VERSIONED_PULL_PREFIX}/{pr_index}/*",
            force=True,
        )

    versions.append(
        PullRequestVersion(version=v_num, base_ref=base.hexsha, head_ref=head.hexsha)
    )
    return True, versions


def git_env(owner: str, reponame: str) -> dict:
    """Build an environment for git to use custom ssh private keys."""
    identity_file = repo_config("ssh_identity_file", owner, reponame)
    if identity_file:
        id_file = Path(identity_file).expanduser()
        if not id_file.exists():
            logging.error(f"{owner}/{reponame}: Cannot find {id_file}")
            raise RetryException()
        return {"GIT_SSH_COMMAND": f"ssh -i {id_file.absolute()} -o IdentitiesOnly=yes"}
    return {}


def gcc_git_descr(repo: git.Repo, commit_ref: str, mode: GccGitDescrWays) -> str:
    """
    An implementation of gcc's git-descr.sh algorith.
    Original implementation: https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=contrib/git-descr.sh;hb=HEAD

    Modes:
      - SHORT: "r<major>-<minor>"
      - LONG: full ref name with 40-char hash
      - VANILLA: includes hash and handles releases
    """
    commit = repo.commit(commit_ref)
    if mode == GccGitDescrWays.SHORT:
        raw_descr = repo.git.describe(
            "--all", "--match", "basepoints/gcc-[0-9]*", commit_ref
        )
        description = raw_descr.removeprefix("tags/")
        if match := BASEPOINT_WITH_PATCH_RE.match(description):
            description = f"r{match.group(1)}-{match.group(2)}"
        elif match := BASEPOINT_WITHOUT_PATCH_RE.match(description):
            description = f"r{match.group(1)}-0"
        else:
            raise RuntimeError(
                f"Cannot trace commit {commit_ref} to a GCC basepoint"
            )  # pragma: no cover
    elif mode == GccGitDescrWays.LONG:
        raw_descr = repo.git.describe(
            "--all", "--abbrev=40", "--match", "basepoints/gcc-[0-9]*", commit_ref
        )
        description = raw_descr.removeprefix("tags/")
        if description.startswith("basepoints/gcc-"):
            description = description.replace("basepoints/gcc-", "r")
        else:
            raise RuntimeError(
                f"Cannot trace commit {commit_ref} to a GCC basepoint"
            )  # pragma: no cover
    elif mode == GccGitDescrWays.VANILLA:
        raw_descr = repo.git.describe(
            "--all", "--abbrev=14", "--match", "basepoints/gcc-[0-9]*", commit_ref
        )
        description = raw_descr.removeprefix("tags/")
        if description.startswith("basepoints/gcc-"):
            description = description.replace("basepoints/gcc-", "r")
        else:
            raise RuntimeError(
                f"Cannot trace commit {commit_ref} to a GCC basepoint"
            )  # pragma: no cover
        if RELEASE_NUM_RE.match(description):
            description = f"{description}-0-g{repo.rev_parse(commit_ref)}"
    else:
        raise RuntimeError("Someone came up with a new descr..")  # pragma: no cover

    if m := RELEASE_REF_RE.match(description):
        release_branch = f"refs/heads/releases/gcc-{m.group(1)}"
    else:
        release_branch = "refs/heads/master"

    try:
        final_commit = repo.commit(release_branch)
    except BadName:
        final_commit = repo.commit("refs/heads/master")

    if repo.git.merge_base(commit, final_commit).strip() != commit.hexsha:
        return ""
    return description


@contextmanager
def local_repo_lock(
    owner: str,
    reponame: str,
    timeout: int = REPO_LOCK_TIMEOUT,
    retry_on_error: bool = False,
):
    """Context manager for a Redis-backed lock."""
    lock = redis.lock.Lock(
        redis_service(), f"local_repo/{owner}/{reponame}", timeout=timeout
    )
    acquired = lock.acquire(blocking=not retry_on_error)
    if not acquired and retry_on_error:
        raise RetryException()
    try:
        yield
    finally:
        if acquired:
            lock.release()


def msgid_of_cover_letter(
    repo: git.Repo, versions: list[PullRequestVersion]
) -> str | None:
    """Retrieve the Message Id of the cover letter of the last version that
    has a posting, as saved in the notes."""
    if len(versions) < 2:
        return None
    for version in reversed(versions[:-1]):
        commit = repo.commit(version.head_ref)
        try:
            note_text = repo.git.notes("--ref=batrachomyomachia", "show", commit.hexsha)
        except git.GitCommandError as e:
            if "no note found" not in e.stderr:
                raise
            continue
        if not note_text:
            return None
        yaml = YAML(typ="safe", pure=True)
        note_data = list(yaml.load(note_text))
        if not note_data:
            return None
        for p in reversed(note_data):
            patch_posting = PatchPosting(**p)
            if patch_posting.version == version.version:
                return patch_posting.cover_msgid
    return None


def pr_information_from_local_clone(
    local_repo: git.Repo,
    owner: str,
    repo: str,
    head_sha: str,
    base_ref: str,
) -> LocalRepoPrInformation:
    """Retrieves information that cannot be fetched via the pull_request REST API.
    Specifically:
    - the real base commit (the pull request returns the initial base commit
      which may be out of date due to rebasing)
    - the gcc commit description
    - a list of commit objects that can be queried."""
    head_commit = local_repo.commit(head_sha)
    real_head_sha = head_commit.hexsha
    # The base.sha points at the original sha when the PR was created
    # If the developer has force pushed changes, we must recalculate the merge base
    # ourselves because forgejo will not send it.
    real_base_sha = local_repo.git.merge_base(f"refs/heads/{base_ref}", head_commit)
    base_commit = local_repo.commit(real_base_sha)
    if repo_config("uses_gcc_descr", owner, repo):
        base_gcc_descr = gcc_git_descr(
            local_repo, real_base_sha, GccGitDescrWays.VANILLA
        )
        head_gcc_descr = gcc_git_descr(local_repo, head_sha, GccGitDescrWays.VANILLA)
    else:
        base_gcc_descr = None
        head_gcc_descr = None
    diff = head_commit.diff(base_commit)
    commits = list(
        reversed(list(local_repo.iter_commits(f"{real_base_sha}..{real_head_sha}")))
    )
    return LocalRepoPrInformation(
        real_head_sha=real_head_sha,
        real_base_sha=real_base_sha,
        base_gcc_descr=base_gcc_descr,
        head_gcc_desc=head_gcc_descr,
        diff=diff,
        commits=commits,
    )


def read_pull_versions(repo: git.Repo, pull_idx: int) -> list[PullRequestVersion]:
    """Read existing pull request versions from refs/versioned_pull."""
    versions: dict[int, PullRequestVersion] = {}
    for ref in repo.refs:
        if m := VERSIONED_PULL_REF_RE.match(ref.path):
            idx = int(m.group(1))
            if idx != pull_idx:
                continue
            ver = int(m.group(2))
            kind = m.group(3)
            pr_ver = versions.setdefault(ver, PullRequestVersion(version=ver))
            if kind == "base":
                pr_ver.base_ref = ref.commit.hexsha
            else:
                pr_ver.head_ref = ref.commit.hexsha
    return sorted(versions.values(), key=lambda v: v.version)


def run_git_format_patch(
    custom_from_addr: str,
    repo: git.Repo,
    patches_dir: Path,
    cover_txt: Path,
    versions: list[PullRequestVersion],
) -> Path:
    """Generate patches with cover letter via `git format-patch`."""
    out_dir = patches_dir / "patches"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        repo.git.git_exec_name,
        "format-patch",
        f"--reroll-count={versions[-1].version}",
        "--attach",
        "--inline",
        f"--from={custom_from_addr}",
        f"--output-directory={out_dir.absolute()}",
        "--cover-letter",
        "--cover-from-description=subject",
        f"--description-file={cover_txt}",
    ]
    if len(versions) >= 2:
        prev = versions[-2]
        cmd.append(f"--range-diff={prev.base_ref}..{prev.head_ref}")
    current = versions[-1]
    cmd.append(f"{current.base_ref}..{current.head_ref}")

    log_path = patches_dir / "git-format-patch.log"
    logging.info(f"Running {shlex.join(cmd)} in {repo.working_dir}")
    with open(log_path, "w") as log_file:
        result = subprocess.run(
            cmd,
            cwd=repo.working_dir,
            stdout=log_file,
            stderr=log_file,
        )
    if result.returncode:
        msg = f"git format-patch failed ({result.returncode}), see {log_path}"
        logging.error(msg)
        raise RuntimeError(msg)
    logging.info(f"Patches generated in {out_dir}")
    return out_dir


def update_repo_branches(
    repo: git.Repo, owner: str, reponame: str, refs_mappings: list[str]
):
    """
    Clone or reuse a bare repo, adding an upstream if configured.
    """
    if "upstream" not in repo.remotes:
        raise RuntimeError(f"{owner}/{reponame} does not have an upstream remote")
    origin = repo.remote("origin")
    upstream = repo.remote("upstream")
    with local_repo_lock(owner, reponame):
        logging.info(f"{owner}/{reponame} update: Fetching refs from upstream")
        # upstream repository beats everything
        upstream.fetch(refspec="refs/*:refs/*", force=True)
        # Except our notes, pull requests and versioned pull requests
        logging.info(
            f"{owner}/{reponame} update: Fetching notes and (versioned) PRs from origin"
        )
        origin.fetch(
            refspec="refs/notes/batrachomyomachia/*:refs/notes/batrachomyomachia/*",
            force=True,
        )
        origin.fetch(refspec="refs/pull/*:refs/pull/*", force=True)
        origin.fetch(
            refspec=f"{VERSIONED_PULL_PREFIX}/*:{VERSIONED_PULL_PREFIX}/*",
            force=True,
        )
        for mapping in refs_mappings:
            logging.info(f"{owner}/{reponame} update: Pushing {mapping} to origin")
            repo.git.push("origin", mapping, "--force")


def update_repo_notes(
    repo: git.Repo,
    owner: str,
    reponame: str,
    commits: list[git.Commit],
    postings: list[PatchPosting],
) -> None:
    """Append patch post information to PR commit notes."""
    with local_repo_lock(owner, reponame):
        repo.remote().fetch("refs/notes/*:refs/notes/*", force=True)
        for commit, post in zip(commits, postings):
            try:
                existing = repo.git.notes(
                    "--ref=batrachomyomachia", "show", commit.hexsha
                )
            except GitCommandError as e:
                if "no note found" in e.stderr:
                    existing = "[]"
                else:
                    raise
            yaml = YAML(typ="safe", pure=True)
            data = list(yaml.load(existing)) or []
            data.append(asdict(post))

            with tempfile.NamedTemporaryFile(
                mode="w+", delete=False, suffix=".yaml"
            ) as tmp:
                yaml.dump(data, tmp)
                repo.git.notes(
                    "--ref=batrachomyomachia",
                    "add",
                    "-f",
                    "-F",
                    tmp.name,
                    commit.hexsha,
                )
        repo.remote().push("refs/notes/*:refs/notes/*", force=True)


def write_versioned_pull_refs(
    repo: git.Repo,
    pr_index: int,
    version: int,
    head: git.Commit,
    base: git.Commit,
) -> None:
    base_ref = f"{VERSIONED_PULL_PREFIX}/{pr_index}/{version}/base"
    head_ref = f"{VERSIONED_PULL_PREFIX}/{pr_index}/{version}/head"
    logging.info(
        f"Storing version refs: {base_ref}, {head_ref} for pr version {pr_index}"
    )
    git.Reference.create(repo, base_ref, base.hexsha)
    git.Reference.create(repo, head_ref, head.hexsha)
