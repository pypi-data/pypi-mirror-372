# pylint: disable=too-many-instance-attributes, too-many-branches, too-many-boolean-expressions
"""Git adapter for OpenDAPI"""

from __future__ import annotations

import re
import subprocess  # nosec: B404
from dataclasses import asdict, dataclass
from typing import List, Optional, Tuple

from opendapi.cli.common import print_encoded_breadcrumbs
from opendapi.defs import ALL_OPENDAPI_SUFFIXES, REFS_PREFIXES, CommitType
from opendapi.logging import logger


def run_git_command(cwd: str, command_split: List[str]) -> str:
    """Run a git command."""
    try:
        return subprocess.check_output(
            command_split,
            cwd=cwd,
        )  # nosec
    except subprocess.CalledProcessError as exc:
        # KBtodo: Figure out why this is not sent to sentry but CI fails
        print_encoded_breadcrumbs(f"git command {command_split}: {exc}")
        raise RuntimeError(f"git command {command_split}: {exc}") from exc


def get_commit_timestamp_str(cwd: str, commit_sha: str) -> str:
    """Get the commit timestamp string."""
    return (
        run_git_command(
            cwd,
            [
                "git",
                "show",
                "--format=%cd",
                "--no-patch",
                "--date=iso-strict",
                commit_sha,
            ],
        )
        .decode("utf-8")
        .strip()
    )


def get_merge_base(cwd: str, current_ref: str, base_ref: str) -> str:
    """Get the merge base of two refs."""
    merge_base = (
        run_git_command(cwd, ["git", "merge-base", current_ref, base_ref])
        .decode("utf-8")
        .strip()
    )
    logger.info("Merge base of %s and %s is %s", current_ref, base_ref, merge_base)
    return merge_base


def get_upstream_commit_sha(cwd: str, ref: str, steps: int) -> str:
    """Get the upstream commit SHA."""
    if steps < 0:
        raise ValueError("Steps must be non-negative")

    upstream_sha = (
        run_git_command(
            cwd,
            ["git", "rev-parse", f"{ref}~{steps}"],
        )
        .decode("utf-8")
        .strip()
    )
    logger.info("Upstream commit SHA of %s~%s is %s", ref, steps, upstream_sha)
    return upstream_sha


def get_checked_out_branch_or_commit(cwd: str) -> str:
    """Get the checked out branch or commit."""
    # if a branch is checked out, returns the branch name, if a commit is, it returns HEAD
    branch_name_or_head = (
        run_git_command(cwd, ["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode("utf-8")
        .strip()
    )
    # if the branch is detached, it returns the commit hash
    if branch_name_or_head == "HEAD":
        return (
            run_git_command(cwd, ["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        )
    return branch_name_or_head


def _get_current_stash_names_with_index(cwd: str) -> List[Tuple[int, str]]:
    return [
        (i, stash.split(": ")[-1])
        for i, stash in enumerate(
            run_git_command(cwd, ["git", "stash", "list"]).decode("utf-8").split("\n")
        )
    ]


def add_named_stash(cwd: str, stash_name: str) -> bool:
    """
    Add a named stash. Note that index not returned
    since it changes with other stashes.

    Returns True if a stash was created, False otherwise.
    """
    # if there is nothing to stash this does not raise or fail, but instead
    # just does not create the named stash
    current_stashes = [stash for _, stash in _get_current_stash_names_with_index(cwd)]
    if stash_name in current_stashes:
        raise ValueError(f"Stash {stash_name} already exists")
    result = (
        run_git_command(
            cwd, ["git", "stash", "save", "--include-untracked", stash_name]
        )
        .decode("utf-8")
        .strip()
    )
    return result != "No local changes to save"


def pop_named_stash(cwd: str, stash_name: str) -> None:
    """Pop a named stash."""
    current_stashes_w_index = _get_current_stash_names_with_index(cwd)
    stash_index = next(
        (i for i, stash in current_stashes_w_index if stash == stash_name),
        None,
    )
    if stash_index is None:
        raise ValueError(f"Stash {stash_name} not found")
    run_git_command(cwd, ["git", "stash", "pop", f"stash@{{{stash_index}}}"])


def get_changed_opendapi_filenames(cwd: str) -> List[str]:
    """Get the list of changed opendapi files."""
    files_patterns = ["*" + suffix for suffix in ALL_OPENDAPI_SUFFIXES]
    all_files_command = [
        "git",
        "status",
        "--porcelain",
        *files_patterns,
    ]
    result = run_git_command(cwd, all_files_command)
    if not result:
        return []
    result = result.decode("utf-8").replace("'", "")
    return [r.split(" ", 2)[-1] for r in result.split("\n") if r]


def add_untracked_opendapi_files(
    cwd: str, files_patterns: Optional[List[str]] = None
) -> int:
    """Add opendapi relevant untracked files to git and return number of files added."""
    files_patterns = files_patterns or [
        "*" + suffix for suffix in ALL_OPENDAPI_SUFFIXES
    ]
    all_files_command = [
        "git",
        "add",
        "--dry-run",
        "--ignore-missing",
        *files_patterns,
    ]
    result = run_git_command(cwd, all_files_command)
    if result:
        result = result.decode("utf-8").replace("'", "")
        all_files = [r.split(" ", 2)[-1] for r in result.split("\n") if r]
        run_git_command(cwd, ["git", "add", *all_files])
        return len(all_files)
    return 0  # pragma: no cover


def get_git_diff_filenames(
    root_dir: str,
    base_ref: str,
    current_ref: Optional[str] = None,
    cached: bool = False,
) -> List[str]:
    """Get the list of files changed between current and main branch"""
    commands = [
        "git",
        "diff",
        *(["--cached"] if cached else []),
        *["--name-only", base_ref],
        *([current_ref] if current_ref else []),
    ]
    files = run_git_command(root_dir, commands)
    return [filename for filename in files.decode("utf-8").split("\n") if filename]


def check_if_uncommitted_changes_exist(cwd: str) -> bool:
    """Check if uncommitted changes exist."""
    if run_git_command(cwd, ["git", "diff", "--name-only"]):
        return True
    return False


def check_if_untracked_changes_exist(cwd: str) -> bool:
    """Check if untracked files exist."""
    if run_git_command(cwd, ["git", "ls-files", "--others", "--exclude-standard"]):
        return True
    return False


def check_if_uncomitted_or_untracked_changes_exist(cwd: str) -> bool:
    """Check if uncommitted or untracked changes exist."""
    return check_if_uncommitted_changes_exist(cwd) or check_if_untracked_changes_exist(
        cwd
    )


class GitCommitStasher:
    """
    Context manager to stash changes while checking out a commit.
    """

    def __init__(self, cwd: str, stash_name: str, commit_sha: str):
        # args
        self.cwd = cwd
        self.stash_name = stash_name
        self.commit_sha = commit_sha
        # internal state
        self.currently_stashed = False
        self.stash_created = False
        self.pre_checkout_sha = None
        # reduce noise about detached head
        run_git_command(
            self.cwd, ["git", "config", "--global", "advice.detachedHead", "false"]
        )

    def _reset(self):
        """
        Reset the state of the stasher.
        """
        run_git_command(self.cwd, ["git", "checkout", self.pre_checkout_sha])

        if self.stash_created:
            pop_named_stash(self.cwd, self.stash_name)

        self.currently_stashed = False
        self.stash_created = False
        self.pre_checkout_sha = None

    def __enter__(self) -> GitCommitStasher:
        if self.currently_stashed:
            raise ValueError("Already stashed")
        self.stash_created = add_named_stash(self.cwd, self.stash_name)
        # sanity check
        if check_if_uncomitted_or_untracked_changes_exist(self.cwd):
            self._reset()
            raise RuntimeError("You have uncommitted or untracked changes after stash")
        self.currently_stashed = True
        self.pre_checkout_sha = get_checked_out_branch_or_commit(self.cwd)
        run_git_command(self.cwd, ["git", "checkout", self.commit_sha])
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not self.currently_stashed:
            raise ValueError("Not stashed")

        try:
            if check_if_uncomitted_or_untracked_changes_exist(self.cwd):
                raise RuntimeError("File changes were detected while stashed.")

        finally:
            self._reset()


@dataclass(frozen=True)
class ChangeTriggerEvent:
    """
    Summary information for git changes
    """

    where: str
    before_change_sha: str = None
    event_type: Optional[str] = None
    after_change_sha: Optional[str] = None
    after_change_sha_timestamp: Optional[str] = None
    repo_api_url: Optional[str] = None
    repo_html_url: Optional[str] = None
    repo_owner: Optional[str] = None
    git_ref: Optional[str] = None
    pull_request_number: Optional[int] = None
    auth_token: Optional[str] = None
    workspace: Optional[str] = None
    head_sha: Optional[str] = None
    repository: Optional[str] = None
    repo_full_name: Optional[str] = None
    pull_request_link: Optional[str] = None
    original_pr_author: Optional[str] = None

    def __post_init__(self):
        """Post init checks"""
        if self.where not in ["local", "github"] or self.before_change_sha is None:
            raise ValueError(
                "Where should be either local or github."
                " Before change SHA is required"
            )

        if self.is_github_event:
            if (
                self.event_type is None
                or self.after_change_sha is None
                or self.repo_api_url is None
                or self.repo_html_url is None
                or self.repo_owner is None
            ):
                raise ValueError(
                    "Event type, after change SHA, repo API URL, repo HTML URL, "
                    "repo owner are required"
                )

            if self.is_pull_request_event:
                if self.pull_request_number is None:
                    raise ValueError("Pull request number is required")
                if self.pull_request_link is None:
                    raise ValueError("Pull request link is required")

        if self.is_push_event:
            if self.git_ref is None:
                raise ValueError("Git ref is required")

    @property
    def is_local_event(self) -> bool:
        """Check if the event is a local event"""
        return self.where == "local"

    @property
    def is_github_event(self) -> bool:
        """Check if the event is a github event"""
        return self.where == "github"

    @property
    def is_pull_request_event(self) -> bool:
        """Check if the event is a pull request event"""
        return self.event_type == "pull_request"

    @property
    def is_push_event(self) -> bool:
        """Check if the event is a push event"""
        return self.event_type == "push"

    @property
    def integration_type(self) -> str:
        """Get the integration type"""
        return "direct" if self.where == "local" else self.where

    @property
    def branch(self) -> Optional[str]:
        """Get the branch"""
        if not self.git_ref:
            return None  # pragma: no cover

        return next(
            (
                re.split(prefix, self.git_ref)[-1]
                for prefix in REFS_PREFIXES
                if re.match(prefix, self.git_ref)
            ),
            self.git_ref,
        )

    @property
    def as_dict(self) -> dict:
        """Get the event as a dictionary"""
        return asdict(self)

    def commit_type_to_sha(
        self, commit_type: CommitType, enforce: bool = True
    ) -> Optional[str]:
        """Get the SHA for the commit type"""
        commit_sha = (
            self.before_change_sha
            if commit_type is CommitType.BASE
            else self.after_change_sha
        )
        if commit_sha is None and enforce:  # pragma: no cover
            raise ValueError("Commit SHA is required")
        return commit_sha
