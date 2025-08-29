# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation
#
# High-level orchestrator scaffold for the GitHub PR -> Gerrit flow.
#
# This module defines the public orchestration surface and typed data models
# used to execute the end-to-end workflow. The major steps are implemented:
# configuration resolution, commit preparation (single or squash), pushing
# to Gerrit, querying results, and posting comments, with a dry-run mode
# for non-destructive validations.
#
# Design principles applied:
# - Single Responsibility: orchestration logic is grouped here; git/exec
#   helpers live in gitutils.py; CLI argument parsing lives in cli.py.
# - Strict typing: all public functions and data models are typed.
# - Central logging: use Python logging; callers can configure handlers.
# - Compatibility: inputs map 1:1 with the existing shell-based action.
#
# Capabilities overview:
# - Invoked by the Typer CLI entrypoint.
# - Reads .gitreview for Gerrit host/port/project when present; otherwise
#   resolves from explicit inputs.
# - Supports both "single commit" and "squash" submission strategies.
# - Pushes via git-review to refs/for/<branch> and manages Change-Id.
# - Queries Gerrit for URL/change-number and updates PR comments.

from __future__ import annotations

import logging
import os
import re
import stat
import urllib.parse
import urllib.request
from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .github_api import build_client
from .github_api import close_pr
from .github_api import create_pr_comment
from .github_api import get_pr_title_body
from .github_api import get_pull
from .github_api import get_recent_change_ids_from_comments
from .github_api import get_repo_from_env
from .github_api import iter_open_pulls
from .gitutils import CommandError
from .gitutils import GitError
from .gitutils import git_cherry_pick
from .gitutils import git_commit_amend
from .gitutils import git_commit_new
from .gitutils import git_config
from .gitutils import git_last_commit_trailers
from .gitutils import git_show
from .gitutils import run_cmd
from .models import GitHubContext
from .models import Inputs


try:
    from pygerrit2 import GerritRestAPI
    from pygerrit2 import HTTPBasicAuth
except ImportError:
    GerritRestAPI = None
    HTTPBasicAuth = None

try:
    from .ssh_discovery import SSHDiscoveryError
    from .ssh_discovery import auto_discover_gerrit_host_keys
except ImportError:
    # Fallback if ssh_discovery module is not available
    auto_discover_gerrit_host_keys = None  # type: ignore[assignment]
    SSHDiscoveryError = Exception  # type: ignore[misc,assignment]


def _is_verbose_mode() -> bool:
    """Check if verbose mode is enabled via environment variable."""
    return os.getenv("G2G_VERBOSE", "").lower() in ("true", "1", "yes")


def _log_exception_conditionally(
    logger: logging.Logger, message: str, *args: Any
) -> None:
    """Log exception with traceback only if verbose mode is enabled."""
    if _is_verbose_mode():
        logger.exception(message, *args)
    else:
        logger.error(message, *args)


log = logging.getLogger("github2gerrit.core")


# Error message constants to comply with TRY003
_MSG_ISSUE_ID_MULTILINE = "Issue ID must be single line"
_MSG_MISSING_PR_CONTEXT = "missing PR context"
_MSG_BAD_REPOSITORY_CONTEXT = "bad repository context"
_MSG_MISSING_GERRIT_SERVER = "missing GERRIT_SERVER"
_MSG_MISSING_GERRIT_PROJECT = "missing GERRIT_PROJECT"
_MSG_PYGERRIT2_REQUIRED_REST = "pygerrit2 is required to query Gerrit REST API"
_MSG_PYGERRIT2_REQUIRED_AUTH = "pygerrit2 is required for HTTP authentication"
_MSG_PYGERRIT2_MISSING = "pygerrit2 missing"
_MSG_PYGERRIT2_AUTH_MISSING = "pygerrit2 auth missing"


def _insert_issue_id_into_commit_message(message: str, issue_id: str) -> str:
    """
    Insert Issue ID into commit message after the first line.

    Format:
    Title line

    Issue-ID: CIMAN-33

    Rest of body...
    """
    if not issue_id.strip():
        return message

    # Validate that Issue ID is a single line string
    cleaned_issue_id = issue_id.strip()
    if "\n" in cleaned_issue_id or "\r" in cleaned_issue_id:
        raise ValueError(_MSG_ISSUE_ID_MULTILINE)

    # Format as proper Issue-ID trailer
    if cleaned_issue_id.startswith("Issue-ID:"):
        issue_line = cleaned_issue_id
    else:
        issue_line = f"Issue-ID: {cleaned_issue_id}"

    lines = message.splitlines()
    if not lines:
        return message

    # Take the first line as title
    title = lines[0]

    # Build new message with Issue ID on third line
    new_lines = [title, "", issue_line]

    # Add rest of the body if it exists
    if len(lines) > 1:
        # Skip empty lines immediately after title to avoid double spacing
        body_start = 1
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        if body_start < len(lines):
            new_lines.append("")  # Empty line before body
            new_lines.extend(lines[body_start:])

    return "\n".join(new_lines)


# ---------------------
# Utility functions
# ---------------------


def _match_first_group(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    if not m:
        return None
    if m.groups():
        return m.group(1)
    return m.group(0)


def _is_valid_change_id(value: str) -> bool:
    # Gerrit Change-Id usually matches I<40-hex> but the shell workflow
    # uses a looser grep. Keep validation permissive for now.
    if not value:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9._-]+", value))


@dataclass(frozen=True)
class GerritInfo:
    host: str
    port: int
    project: str


@dataclass(frozen=True)
class RepoNames:
    # Gerrit repo path, e.g. "releng/builder"
    project_gerrit: str
    # GitHub repo name (no org/owner), e.g. "releng-builder"
    project_github: str


@dataclass(frozen=True)
class PreparedChange:
    # One or more Change-Id values that will be (or were) pushed.
    change_ids: list[str]
    # The commit shas created/pushed to Gerrit. May be empty until queried.
    commit_shas: list[str]


@dataclass(frozen=True)
class SubmissionResult:
    # URLs of created/updated Gerrit changes.
    change_urls: list[str]
    # Numeric change-ids in Gerrit (change number).
    change_numbers: list[str]
    # Associated patch set commit shas in Gerrit (if available).
    commit_shas: list[str]


class OrchestratorError(RuntimeError):
    """Raised on unrecoverable orchestration failures."""


class Orchestrator:
    """Coordinates the end-to-end PR -> Gerrit submission flow.

    Responsibilities (to be implemented):
    - Discover and validate environment and inputs.
    - Derive Gerrit connection and project names.
    - Prepare commits (single or squashed) and manage Change-Id.
    - Push to Gerrit using git-review with topic and reviewers.
    - Query Gerrit for URL/change-number and produce outputs.
    - Comment on the PR and optionally close it.
    """

    def __init__(
        self,
        *,
        workspace: Path,
    ) -> None:
        self.workspace = workspace
        # SSH configuration paths (set by _setup_ssh)
        self._ssh_key_path: Path | None = None
        self._ssh_known_hosts_path: Path | None = None

    # ---------------
    # Public API
    # ---------------

    def execute(
        self,
        inputs: Inputs,
        gh: GitHubContext,
    ) -> SubmissionResult:
        """Run the full pipeline and return a structured result.

        This method defines the high-level call order. Sub-steps are
        placeholders and must be implemented with real logic. Until then,
        this raises NotImplementedError after logging the intended plan.
        """
        log.info("Starting PR -> Gerrit pipeline")
        self._guard_pull_request_context(gh)

        # Initialize git repository in workspace if it doesn't exist
        if not (self.workspace / ".git").exists():
            self._setup_git_workspace(inputs, gh)

        gitreview = self._read_gitreview(self.workspace / ".gitreview", gh)
        repo_names = self._derive_repo_names(gitreview, gh)
        gerrit = self._resolve_gerrit_info(gitreview, inputs, repo_names)

        if inputs.dry_run:
            # Perform preflight validations and exit without making changes
            self._dry_run_preflight(
                gerrit=gerrit, inputs=inputs, gh=gh, repo=repo_names
            )
            log.info("Dry run complete; skipping write operations to Gerrit")
            return SubmissionResult(
                change_urls=[], change_numbers=[], commit_shas=[]
            )
        self._setup_ssh(inputs, gerrit)

        if inputs.submit_single_commits:
            prep = self._prepare_single_commits(inputs, gh, gerrit)
        else:
            prep = self._prepare_squashed_commit(inputs, gh, gerrit)

        self._configure_git(gerrit, inputs)
        self._apply_pr_title_body_if_requested(inputs, gh)

        self._push_to_gerrit(
            gerrit=gerrit,
            repo=repo_names,
            branch=self._resolve_target_branch(),
            reviewers=self._resolve_reviewers(inputs),
            single_commits=inputs.submit_single_commits,
        )

        result = self._query_gerrit_for_results(
            gerrit=gerrit,
            repo=repo_names,
            change_ids=prep.change_ids,
        )

        self._add_backref_comment_in_gerrit(
            gerrit=gerrit,
            repo=repo_names,
            branch=self._resolve_target_branch(),
            commit_shas=result.commit_shas,
            gh=gh,
        )

        self._comment_on_pull_request(gh, gerrit, result)

        self._close_pull_request_if_required(gh)

        log.info("Pipeline complete: %s", result)
        self._cleanup_ssh()
        return result

    # ---------------
    # Step scaffolds
    # ---------------

    def _guard_pull_request_context(self, gh: GitHubContext) -> None:
        if gh.pr_number is None:
            raise OrchestratorError(_MSG_MISSING_PR_CONTEXT)
        log.debug("PR context OK: #%s", gh.pr_number)

    def _parse_gitreview_text(self, text: str) -> GerritInfo | None:
        host = _match_first_group(r"(?m)^host=(.+)$", text)
        port_s = _match_first_group(r"(?m)^port=(\d+)$", text)
        proj = _match_first_group(r"(?m)^project=(.+)$", text)
        if host and proj:
            project = proj.removesuffix(".git")
            port = int(port_s) if port_s else 29418
            return GerritInfo(
                host=host.strip(),
                port=port,
                project=project.strip(),
            )
        return None

    def _read_gitreview(
        self,
        path: Path,
        gh: GitHubContext | None = None,
    ) -> GerritInfo | None:
        """Read .gitreview and return GerritInfo if present.

        Expected keys:
          host=<hostname>
          port=<port>
          project=<repo/path>.git
        """
        if not path.exists():
            log.info(".gitreview not found locally; attempting remote fetch")
            # If invoked via direct URL or in environments with a token,
            # attempt to read .gitreview from the repository using the API.
            try:
                client = build_client()
                repo_obj: Any = get_repo_from_env(client)
                # Prefer a specific ref when available; otherwise default branch
                ref = os.getenv("GITHUB_HEAD_REF") or os.getenv("GITHUB_SHA")
                if ref:
                    content = repo_obj.get_contents(".gitreview", ref=ref)
                else:
                    content = repo_obj.get_contents(".gitreview")
                text_remote = (
                    getattr(content, "decoded_content", b"") or b""
                ).decode("utf-8")
                info_remote = self._parse_gitreview_text(text_remote)
                if info_remote:
                    log.debug("Parsed remote .gitreview: %s", info_remote)
                    return info_remote
                log.info("Remote .gitreview missing required keys; ignoring")
            except Exception as exc:
                log.debug("Remote .gitreview not available: %s", exc)
            # Attempt raw.githubusercontent.com as a fallback
            try:
                repo_full = (
                    (
                        gh.repository
                        if gh
                        else os.getenv("GITHUB_REPOSITORY", "")
                    )
                    or ""
                ).strip()
                branches: list[str] = []
                # Prefer PR head/base refs via GitHub API when running
                # from a direct URL when a token is available
                try:
                    if (
                        gh
                        and gh.pr_number
                        and os.getenv("G2G_TARGET_URL")
                        and (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN"))
                    ):
                        client = build_client()
                        repo_obj = get_repo_from_env(client)
                        pr_obj = get_pull(repo_obj, int(gh.pr_number))
                        api_head = str(
                            getattr(
                                getattr(pr_obj, "head", object()), "ref", ""
                            )
                            or ""
                        )
                        api_base = str(
                            getattr(
                                getattr(pr_obj, "base", object()), "ref", ""
                            )
                            or ""
                        )
                        if api_head:
                            branches.append(api_head)
                        if api_base:
                            branches.append(api_base)
                except Exception as exc_api:
                    log.debug(
                        "Could not resolve PR refs via API for .gitreview: %s",
                        exc_api,
                    )
                if gh and gh.head_ref:
                    branches.append(gh.head_ref)
                if gh and gh.base_ref:
                    branches.append(gh.base_ref)
                branches.extend(["master", "main"])
                tried: set[str] = set()
                for br in branches:
                    if not br or br in tried:
                        continue
                    tried.add(br)
                    url = (
                        f"https://raw.githubusercontent.com/"
                        f"{repo_full}/refs/heads/{br}/.gitreview"
                    )
                    parsed = urllib.parse.urlparse(url)
                    if (
                        parsed.scheme != "https"
                        or parsed.netloc != "raw.githubusercontent.com"
                    ):
                        continue
                    log.info("Fetching .gitreview via raw URL: %s", url)
                    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
                        text_remote = resp.read().decode("utf-8")
                    info_remote = self._parse_gitreview_text(text_remote)
                    if info_remote:
                        log.debug("Parsed remote .gitreview: %s", info_remote)
                        return info_remote
            except Exception as exc2:
                log.debug("Raw .gitreview fetch failed: %s", exc2)
            log.info("Remote .gitreview not available via API or HTTP")
            log.info("Falling back to inputs/env")
            return None

        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            msg = f"failed to read .gitreview: {exc}"
            raise OrchestratorError(msg) from exc
        info_local = self._parse_gitreview_text(text)
        if not info_local:
            msg = "invalid .gitreview: missing host/project"
            raise OrchestratorError(msg)
        log.debug("Parsed .gitreview: %s", info_local)
        return info_local

    def _derive_repo_names(
        self,
        gitreview: GerritInfo | None,
        gh: GitHubContext,
    ) -> RepoNames:
        """Compute Gerrit and GitHub repo names following existing rules.

        - Gerrit project remains as-is (from .gitreview when present).
        - GitHub repo name is Gerrit project path with '/' replaced by '-'.
          If .gitreview is not available, derive from GITHUB_REPOSITORY.
        """
        if gitreview:
            gerrit_name = gitreview.project
            github_name = gerrit_name.replace("/", "-")
            names = RepoNames(
                project_gerrit=gerrit_name,
                project_github=github_name,
            )
            log.debug("Derived names from .gitreview: %s", names)
            return names

        # Fallback: use the repository name portion only.
        repo_full = gh.repository
        if not repo_full or "/" not in repo_full:
            raise OrchestratorError(_MSG_BAD_REPOSITORY_CONTEXT)
        owner, name = repo_full.split("/", 1)
        # Fallback: map all '-' to '/' for Gerrit path (e.g., 'my/repo/name')
        gerrit_name = name.replace("-", "/")
        names = RepoNames(project_gerrit=gerrit_name, project_github=name)
        log.debug("Derived names from context: %s", names)
        return names

    def _resolve_gerrit_info(
        self,
        gitreview: GerritInfo | None,
        inputs: Inputs,
        repo: RepoNames,
    ) -> GerritInfo:
        """Resolve Gerrit connection info from .gitreview or inputs."""
        if gitreview:
            return gitreview

        host = inputs.gerrit_server.strip()
        if not host:
            raise OrchestratorError(_MSG_MISSING_GERRIT_SERVER)
        port_s = inputs.gerrit_server_port.strip() or "29418"
        try:
            port = int(port_s)
        except ValueError as exc:
            msg = "bad GERRIT_SERVER_PORT"
            raise OrchestratorError(msg) from exc

        project = inputs.gerrit_project.strip()
        if not project:
            if inputs.dry_run:
                project = repo.project_gerrit
                log.info("Dry run: using derived Gerrit project '%s'", project)
            elif os.getenv("G2G_TARGET_URL", "").strip():
                project = repo.project_gerrit
                log.info(
                    "Using derived Gerrit project '%s' from repository name",
                    project,
                )
            else:
                raise OrchestratorError(_MSG_MISSING_GERRIT_PROJECT)

        info = GerritInfo(host=host, port=port, project=project)
        log.debug("Resolved Gerrit info: %s", info)
        return info

    def _setup_ssh(self, inputs: Inputs, gerrit: GerritInfo) -> None:
        """Set up temporary SSH configuration for Gerrit access.

        This method creates tool-specific SSH files in the workspace without
        modifying user SSH configuration. Key features:

        - Creates temporary SSH key and known_hosts files
        - Uses GIT_SSH_COMMAND to specify exact SSH behavior
        - Prevents SSH agent scanning with IdentitiesOnly=yes
        - Host-specific configuration without global impact
        - Automatic cleanup when done

        Does not modify user files.
        """
        if not inputs.gerrit_ssh_privkey_g2g:
            log.debug("SSH private key not provided, skipping SSH setup")
            return

        # Auto-discover host keys if not provided
        effective_known_hosts = inputs.gerrit_known_hosts
        if (
            not effective_known_hosts
            and auto_discover_gerrit_host_keys is not None
        ):
            log.info(
                "GERRIT_KNOWN_HOSTS not provided, attempting auto-discovery..."
            )
            try:
                discovered_keys = auto_discover_gerrit_host_keys(
                    gerrit_hostname=gerrit.host,
                    gerrit_port=gerrit.port,
                    organization=inputs.organization,
                    save_to_config=True,
                )
                if discovered_keys:
                    effective_known_hosts = discovered_keys
                    log.info(
                        "Successfully auto-discovered SSH host keys for %s:%d",
                        gerrit.host,
                        gerrit.port,
                    )
                else:
                    log.warning(
                        "Auto-discovery failed, SSH host key verification may "
                        "fail"
                    )
            except Exception as exc:
                log.warning("SSH host key auto-discovery failed: %s", exc)

        if not effective_known_hosts:
            log.debug(
                "No SSH host keys available (manual or auto-discovered), "
                "skipping SSH setup"
            )
            return

        log.info("Setting up temporary SSH configuration for Gerrit")
        log.debug("Using workspace-specific SSH files to avoid user changes")

        # Create tool-specific SSH directory in workspace to avoid touching
        # user files
        tool_ssh_dir = self.workspace / ".ssh-g2g"
        tool_ssh_dir.mkdir(mode=0o700, exist_ok=True)

        # Write SSH private key to tool-specific location
        key_path = tool_ssh_dir / "gerrit_key"
        with open(key_path, "w", encoding="utf-8") as f:
            f.write(inputs.gerrit_ssh_privkey_g2g.strip() + "\n")
        key_path.chmod(0o600)
        log.debug("SSH private key written to %s", key_path)
        log.debug("Key file is tool-specific and won't interfere with user SSH")

        # Write known hosts to tool-specific location
        known_hosts_path = tool_ssh_dir / "known_hosts"
        with open(known_hosts_path, "w", encoding="utf-8") as f:
            f.write(effective_known_hosts.strip() + "\n")
        known_hosts_path.chmod(0o644)
        log.debug("Known hosts written to %s", known_hosts_path)
        log.debug("Using isolated known_hosts to prevent user conflicts")

        # Store paths for later use in git commands
        self._ssh_key_path = key_path
        self._ssh_known_hosts_path = known_hosts_path

    @property
    def _git_ssh_command(self) -> str | None:
        """Generate GIT_SSH_COMMAND for secure, isolated SSH configuration.

        This prevents SSH from scanning the user's SSH agent or using
        unintended keys by setting IdentitiesOnly=yes and specifying
        exact key and known_hosts files.
        """
        if not self._ssh_key_path or not self._ssh_known_hosts_path:
            return None

        # Build SSH command with strict options to prevent key scanning
        ssh_options = [
            f"-i {self._ssh_key_path}",
            f"-o UserKnownHostsFile={self._ssh_known_hosts_path}",
            "-o IdentitiesOnly=yes",  # Critical: prevents SSH agent scanning
            "-o StrictHostKeyChecking=yes",
            "-o PasswordAuthentication=no",
            "-o PubkeyAcceptedKeyTypes=+ssh-rsa",
            "-o ConnectTimeout=10",
        ]

        ssh_cmd = f"ssh {' '.join(ssh_options)}"
        masked_cmd = ssh_cmd.replace(str(self._ssh_key_path), "[KEY_PATH]")
        log.debug("Generated SSH command: %s", masked_cmd)
        return ssh_cmd

    def _cleanup_ssh(self) -> None:
        """Clean up temporary SSH files created by this tool.

        Removes the workspace-specific .ssh-g2g directory and all contents.
        This ensures no temporary files are left behind.
        """
        if not hasattr(self, "_ssh_key_path") or not hasattr(
            self, "_ssh_known_hosts_path"
        ):
            return

        try:
            # Remove temporary SSH directory and all contents
            tool_ssh_dir = self.workspace / ".ssh-g2g"
            if tool_ssh_dir.exists():
                import shutil

                shutil.rmtree(tool_ssh_dir)
                log.debug(
                    "Cleaned up temporary SSH directory: %s", tool_ssh_dir
                )
        except Exception as exc:
            log.warning("Failed to clean up temporary SSH files: %s", exc)

    def _configure_git(
        self,
        gerrit: GerritInfo,
        inputs: Inputs,
    ) -> None:
        """Set git global config and initialize git-review if needed."""
        log.info("Configuring git and git-review for %s", gerrit.host)
        # Prefer repo-local config; fallback to global if needed
        try:
            git_config(
                "gitreview.username",
                inputs.gerrit_ssh_user_g2g,
                global_=False,
                cwd=self.workspace,
            )
        except GitError:
            git_config(
                "gitreview.username", inputs.gerrit_ssh_user_g2g, global_=True
            )
        try:
            git_config(
                "user.name",
                inputs.gerrit_ssh_user_g2g,
                global_=False,
                cwd=self.workspace,
            )
        except GitError:
            git_config("user.name", inputs.gerrit_ssh_user_g2g, global_=True)
        try:
            git_config(
                "user.email",
                inputs.gerrit_ssh_user_g2g_email,
                global_=False,
                cwd=self.workspace,
            )
        except GitError:
            git_config(
                "user.email", inputs.gerrit_ssh_user_g2g_email, global_=True
            )

        # Ensure git-review host/port/project are configured
        # when .gitreview is absent
        try:
            git_config(
                "gitreview.hostname",
                gerrit.host,
                global_=False,
                cwd=self.workspace,
            )
            git_config(
                "gitreview.port",
                str(gerrit.port),
                global_=False,
                cwd=self.workspace,
            )
            git_config(
                "gitreview.project",
                gerrit.project,
                global_=False,
                cwd=self.workspace,
            )
        except GitError:
            git_config("gitreview.hostname", gerrit.host, global_=True)
            git_config("gitreview.port", str(gerrit.port), global_=True)
            git_config("gitreview.project", gerrit.project, global_=True)

        # Add 'gerrit' remote if missing (required by git-review)
        try:
            run_cmd(
                ["git", "config", "--get", "remote.gerrit.url"],
                cwd=self.workspace,
            )
        except CommandError:
            ssh_user = inputs.gerrit_ssh_user_g2g.strip()
            remote_url = (
                f"ssh://{ssh_user}@{gerrit.host}:{gerrit.port}/{gerrit.project}"
            )
            log.info("Adding 'gerrit' remote: %s", remote_url)
            # Use our specific SSH configuration for adding remote
            env = (
                {"GIT_SSH_COMMAND": self._git_ssh_command}
                if self._git_ssh_command
                else None
            )
            run_cmd(
                ["git", "remote", "add", "gerrit", remote_url],
                check=False,
                cwd=self.workspace,
                env=env,
            )

        # Workaround for submodules commit-msg hook
        hooks_path = run_cmd(
            ["git", "rev-parse", "--show-toplevel"], cwd=self.workspace
        ).stdout.strip()
        try:
            git_config(
                "core.hooksPath",
                str(Path(hooks_path) / ".git" / "hooks"),
                cwd=self.workspace,
            )
        except GitError:
            git_config(
                "core.hooksPath",
                str(Path(hooks_path) / ".git" / "hooks"),
                global_=True,
            )
        # Initialize git-review (copies commit-msg hook)
        try:
            # Use our specific SSH configuration for git-review setup
            env = (
                {"GIT_SSH_COMMAND": self._git_ssh_command}
                if self._git_ssh_command
                else None
            )
            run_cmd(["git", "review", "-s", "-v"], cwd=self.workspace, env=env)
        except CommandError as exc:
            msg = f"Failed to initialize git-review: {exc}"
            raise OrchestratorError(msg) from exc

    def _prepare_single_commits(
        self,
        inputs: Inputs,
        gh: GitHubContext,
        gerrit: GerritInfo,
    ) -> PreparedChange:
        """Cherry-pick commits one-by-one and ensure Change-Id is present."""
        log.info("Preparing single-commit submission for PR #%s", gh.pr_number)
        branch = self._resolve_target_branch()
        # Determine commit range: commits in HEAD not in base branch
        base_ref = f"origin/{branch}"
        # Use our SSH command for git operations that might need SSH
        env = (
            {"GIT_SSH_COMMAND": self._git_ssh_command}
            if self._git_ssh_command
            else None
        )
        run_cmd(["git", "fetch", "origin", branch], cwd=self.workspace, env=env)
        revs = run_cmd(
            ["git", "rev-list", "--reverse", f"{base_ref}..HEAD"],
            cwd=self.workspace,
        ).stdout
        commit_list = [c for c in revs.splitlines() if c.strip()]
        if not commit_list:
            log.info("No commits to submit; returning empty PreparedChange")
            return PreparedChange(change_ids=[], commit_shas=[])
        # Create temp branch from base sha; export for downstream
        base_sha = run_cmd(
            ["git", "rev-parse", base_ref], cwd=self.workspace
        ).stdout.strip()
        tmp_branch = f"g2g_tmp_{gh.pr_number or 'pr'!s}_{os.getpid()}"
        os.environ["G2G_TMP_BRANCH"] = tmp_branch
        run_cmd(
            ["git", "checkout", "-b", tmp_branch, base_sha], cwd=self.workspace
        )
        change_ids: list[str] = []
        for csha in commit_list:
            run_cmd(["git", "checkout", tmp_branch], cwd=self.workspace)
            git_cherry_pick(csha, cwd=self.workspace)
            # Preserve author of the original commit
            author = run_cmd(
                ["git", "show", "-s", "--pretty=format:%an <%ae>", csha],
                cwd=self.workspace,
            ).stdout.strip()
            git_commit_amend(
                author=author, no_edit=True, signoff=True, cwd=self.workspace
            )
            # Extract newly added Change-Id from last commit trailers
            trailers = git_last_commit_trailers(
                keys=["Change-Id"], cwd=self.workspace
            )
            for cid in trailers.get("Change-Id", []):
                if cid:
                    change_ids.append(cid)
            # Return to base branch for next iteration context
            run_cmd(["git", "checkout", branch], cwd=self.workspace)
        # Deduplicate while preserving order
        seen = set()
        uniq_ids = []
        for cid in change_ids:
            if cid not in seen:
                uniq_ids.append(cid)
                seen.add(cid)
        run_cmd(["git", "log", "-n3", tmp_branch], cwd=self.workspace)
        if uniq_ids:
            log.info(
                "Generated %d unique Change-ID(s) for PR #%s: %s",
                len(uniq_ids),
                gh.pr_number,
                ", ".join(uniq_ids),
            )
        else:
            log.warning("No Change-IDs generated for PR #%s", gh.pr_number)
        return PreparedChange(change_ids=uniq_ids, commit_shas=[])

    def _prepare_squashed_commit(
        self,
        inputs: Inputs,
        gh: GitHubContext,
        gerrit: GerritInfo,
    ) -> PreparedChange:
        """Squash PR commits into a single commit and handle Change-Id."""
        log.info("Preparing squashed commit for PR #%s", gh.pr_number)
        branch = self._resolve_target_branch()
        env = (
            {"GIT_SSH_COMMAND": self._git_ssh_command}
            if self._git_ssh_command
            else None
        )
        run_cmd(["git", "fetch", "origin", branch], cwd=self.workspace, env=env)
        base_ref = f"origin/{branch}"
        base_sha = run_cmd(
            ["git", "rev-parse", base_ref], cwd=self.workspace
        ).stdout.strip()
        head_sha = run_cmd(
            ["git", "rev-parse", "HEAD"], cwd=self.workspace
        ).stdout.strip()

        # Create temp branch from base and merge-squash PR head
        tmp_branch = f"g2g_tmp_{gh.pr_number or 'pr'!s}_{os.getpid()}"
        os.environ["G2G_TMP_BRANCH"] = tmp_branch
        run_cmd(
            ["git", "checkout", "-b", tmp_branch, base_sha], cwd=self.workspace
        )
        run_cmd(["git", "merge", "--squash", head_sha], cwd=self.workspace)

        def _collect_log_lines() -> list[str]:
            body = run_cmd(
                [
                    "git",
                    "log",
                    "--format=%B",
                    "--reverse",
                    f"{base_ref}..{head_sha}",
                ],
                cwd=self.workspace,
            ).stdout
            return [ln for ln in body.splitlines() if ln.strip()]

        def _parse_message_parts(
            lines: list[str],
        ) -> tuple[
            list[str],
            list[str],
            list[str],
        ]:
            change_ids: list[str] = []
            signed_off: list[str] = []
            message_lines: list[str] = []
            in_metadata_section = False
            for ln in lines:
                if ln.strip() in ("---", "```") or ln.startswith(
                    "updated-dependencies:"
                ):
                    in_metadata_section = True
                    continue
                if in_metadata_section:
                    if ln.startswith(("- dependency-", "  dependency-")):
                        continue
                    if (
                        not ln.startswith(("  ", "-", "dependency-"))
                        and ln.strip()
                    ):
                        in_metadata_section = False
                if ln.startswith("Change-Id:"):
                    cid = ln.split(":", 1)[1].strip()
                    if cid:
                        change_ids.append(cid)
                    continue
                if ln.startswith("Signed-off-by:"):
                    signed_off.append(ln)
                    continue
                if not in_metadata_section:
                    message_lines.append(ln)
            signed_off = sorted(set(signed_off))
            return message_lines, signed_off, change_ids

        def _clean_title_line(title_line: str) -> str:
            # Remove markdown links
            title_line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title_line)
            # Remove trailing ellipsis/truncation
            title_line = re.sub(r"\s*[.]{3,}.*$", "", title_line)
            # Split on common separators to avoid leaking body content
            for separator in [". Bumps ", " Bumps ", ". - ", " - "]:
                if separator in title_line:
                    title_line = title_line.split(separator)[0].strip()
                    break
            # Remove simple markdown/formatting artifacts
            title_line = re.sub(r"[*_`]", "", title_line).strip()
            if len(title_line) > 100:
                break_points = [". ", "! ", "? ", " - ", ": "]
                for bp in break_points:
                    if bp in title_line[:100]:
                        title_line = title_line[
                            : title_line.index(bp) + len(bp.strip())
                        ]
                        break
                else:
                    words = title_line[:100].split()
                    title_line = (
                        " ".join(words[:-1])
                        if len(words) > 1
                        else title_line[:100].rstrip()
                    )
            return title_line

        def _build_clean_message_lines(message_lines: list[str]) -> list[str]:
            if not message_lines:
                return []
            title_line = _clean_title_line(message_lines[0].strip())
            out: list[str] = [title_line]
            if len(message_lines) > 1:
                body_start = 1
                while (
                    body_start < len(message_lines)
                    and not message_lines[body_start].strip()
                ):
                    body_start += 1
                if body_start < len(message_lines):
                    out.append("")
                    out.extend(message_lines[body_start:])
            return out

        def _maybe_reuse_change_id(pr_str: str) -> str:
            reuse = ""
            sync_all_prs = (
                os.getenv("SYNC_ALL_OPEN_PRS", "false").lower() == "true"
            )
            if (
                not sync_all_prs
                and gh.event_name == "pull_request_target"
                and gh.event_action in ("reopened", "synchronize")
            ):
                try:
                    client = build_client()
                    repo = get_repo_from_env(client)
                    pr_obj = get_pull(repo, int(pr_str))
                    cand = get_recent_change_ids_from_comments(
                        pr_obj, max_comments=50
                    )
                    if cand:
                        reuse = cand[-1]
                        log.debug(
                            "Reusing Change-ID %s for PR #%s (single-PR mode)",
                            reuse,
                            pr_str,
                        )
                except Exception:
                    reuse = ""
            elif sync_all_prs:
                log.debug(
                    "Skipping Change-ID reuse for PR #%s (multi-PR mode)",
                    pr_str,
                )
            return reuse

        def _compose_commit_message(
            lines_in: list[str],
            signed_off: list[str],
            reuse_cid: str,
        ) -> str:
            from .duplicate_detection import DuplicateDetector

            msg = "\n".join(lines_in).strip()
            msg = _insert_issue_id_into_commit_message(msg, inputs.issue_id)
            github_hash = DuplicateDetector._generate_github_change_hash(gh)
            msg += f"\n\nGitHub-Hash: {github_hash}"
            if signed_off:
                msg += "\n\n" + "\n".join(signed_off)
            if reuse_cid:
                msg += f"\n\nChange-Id: {reuse_cid}"
            return msg

        # Build message parts
        raw_lines = _collect_log_lines()
        message_lines, signed_off, _existing_cids = _parse_message_parts(
            raw_lines
        )
        clean_lines = _build_clean_message_lines(message_lines)
        pr_str = str(gh.pr_number or "").strip()
        reuse_cid = _maybe_reuse_change_id(pr_str)
        commit_msg = _compose_commit_message(clean_lines, signed_off, reuse_cid)

        # Preserve primary author from the PR head commit
        author = run_cmd(
            ["git", "show", "-s", "--pretty=format:%an <%ae>", head_sha],
            cwd=self.workspace,
        ).stdout.strip()
        git_commit_new(
            message=commit_msg,
            author=author,
            signoff=True,
            cwd=self.workspace,
        )

        # Debug: Check commit message after creation
        actual_msg = run_cmd(
            ["git", "show", "-s", "--pretty=format:%B", "HEAD"],
            cwd=self.workspace,
        ).stdout.strip()
        log.debug("Commit message after creation:\n%s", actual_msg)

        # Ensure Change-Id via commit-msg hook (amend if needed)
        cids = self._ensure_change_id_present(gerrit, author)
        if cids:
            log.info(
                "Generated Change-ID(s) for PR #%s: %s",
                gh.pr_number,
                ", ".join(cids),
            )
        else:
            log.warning("No Change-ID generated for PR #%s", gh.pr_number)
        return PreparedChange(change_ids=cids, commit_shas=[])

    def _apply_pr_title_body_if_requested(
        self,
        inputs: Inputs,
        gh: GitHubContext,
    ) -> None:
        """Optionally replace commit message with PR title/body."""
        if not inputs.use_pr_as_commit:
            log.debug("USE_PR_AS_COMMIT disabled; skipping")
            return
        log.info("Applying PR title/body to commit for PR #%s", gh.pr_number)
        pr = str(gh.pr_number or "").strip()
        if not pr:
            return
        # Fetch PR title/body via GitHub API (PyGithub)
        client = build_client()
        repo = get_repo_from_env(client)
        pr_obj = get_pull(repo, int(pr))
        title, body = get_pr_title_body(pr_obj)
        title = (title or "").strip()
        body = (body or "").strip()

        # Clean up title to ensure it's a proper first line for commit message
        if title:
            # Remove markdown links like [text](url) and keep just the text
            title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
            # Remove any trailing ellipsis or truncation indicators
            title = re.sub(r"\s*[.]{3,}.*$", "", title)
            # Ensure title doesn't accidentally contain body content
            # Split on common separators and take only the first meaningful part
            for separator in [". Bumps ", " Bumps ", ". - ", " - "]:
                if separator in title:
                    title = title.split(separator)[0].strip()
                    break
            # Remove any remaining markdown or formatting artifacts
            title = re.sub(r"[*_`]", "", title)
            title = title.strip()

        # Compose message; preserve any Signed-off-by lines
        current_body = git_show("HEAD", fmt="%B")
        signed = [
            ln
            for ln in current_body.splitlines()
            if ln.startswith("Signed-off-by:")
        ]
        msg_parts = [title, "", body] if title or body else [current_body]
        commit_message = "\n".join(msg_parts).strip()

        # Add Issue-ID if provided
        commit_message = _insert_issue_id_into_commit_message(
            commit_message, inputs.issue_id
        )

        if signed:
            commit_message += "\n\n" + "\n".join(signed)
        author = run_cmd(
            ["git", "show", "-s", "--pretty=format:%an <%ae>", "HEAD"]
        ).stdout.strip()
        git_commit_amend(
            no_edit=False,
            signoff=not bool(signed),
            author=author,
            message=commit_message,
        )

    def _push_to_gerrit(
        self,
        *,
        gerrit: GerritInfo,
        repo: RepoNames,
        branch: str,
        reviewers: str,
        single_commits: bool,
    ) -> None:
        """Push prepared commit(s) to Gerrit using git-review."""
        log.info(
            "Pushing changes to Gerrit %s:%s project=%s branch=%s",
            gerrit.host,
            gerrit.port,
            repo.project_gerrit,
            branch,
        )
        log.debug("Starting git review push operation...")
        if single_commits:
            tmp_branch = os.getenv("G2G_TMP_BRANCH", "tmp_branch")
            run_cmd(["git", "checkout", tmp_branch], cwd=self.workspace)
        prefix = os.getenv("G2G_TOPIC_PREFIX", "GH").strip() or "GH"
        pr_num = os.getenv("PR_NUMBER", "").strip()
        if pr_num:
            topic = f"{prefix}-{repo.project_github}-{pr_num}"
        else:
            topic = f"{prefix}-{repo.project_github}"
        try:
            args = [
                "git",
                "review",
                "--yes",
                "-v",
                "-t",
                topic,
            ]
            revs = [
                r.strip() for r in (reviewers or "").split(",") if r.strip()
            ]
            for r in revs:
                args.extend(["--reviewer", r])
            # Branch as positional argument (not a flag)
            args.append(branch)

            # Use our specific SSH configuration
            env = (
                {"GIT_SSH_COMMAND": self._git_ssh_command}
                if self._git_ssh_command
                else None
            )
            log.debug("Executing git review command: %s", " ".join(args))
            run_cmd(args, cwd=self.workspace, env=env)
            log.info("Successfully pushed changes to Gerrit")
        except CommandError as exc:
            # Analyze the specific failure reason from git review output
            error_details = self._analyze_gerrit_push_failure(exc)
            _log_exception_conditionally(
                log, "Gerrit push failed: %s", error_details
            )
            msg = (
                f"Failed to push changes to Gerrit with git-review: "
                f"{error_details}"
            )
            raise OrchestratorError(msg) from exc
        # Cleanup temporary branch used during preparation
        tmp_branch = (os.getenv("G2G_TMP_BRANCH", "") or "").strip()
        if tmp_branch:
            # Switch back to the target branch, then delete the temp branch
            run_cmd(
                ["git", "checkout", f"origin/{branch}"],
                check=False,
                cwd=self.workspace,
            )
            run_cmd(
                ["git", "branch", "-D", tmp_branch],
                check=False,
                cwd=self.workspace,
            )

    def _analyze_gerrit_push_failure(self, exc: CommandError) -> str:
        """Analyze git review failure and provide helpful error message."""
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        combined_output = f"{stdout}\n{stderr}"
        combined_lower = combined_output.lower()

        # Check for SSH host key verification failures first
        if (
            "host key verification failed" in combined_lower
            or "no ed25519 host key is known" in combined_lower
            or "no rsa host key is known" in combined_lower
            or "no ecdsa host key is known" in combined_lower
        ):
            return (
                "SSH host key verification failed. The GERRIT_KNOWN_HOSTS "
                "value is missing or contains an outdated host key for the "
                "Gerrit server. The tool will attempt to auto-discover "
                "host keys "
                "on the next run, or you can manually run "
                "'ssh-keyscan -p 29418 <gerrit-host>' "
                "to get the current host keys."
            )
        elif (
            "authenticity of host" in combined_lower
            and "can't be established" in combined_lower
        ):
            return (
                "SSH host key unknown. The GERRIT_KNOWN_HOSTS value does not "
                "contain the host key for the Gerrit server. "
                "The tool will attempt "
                "to auto-discover host keys on the next run, or you can "
                "manually run "
                "'ssh-keyscan -p 29418 <gerrit-host>' to get the host keys."
            )
        # Check for specific SSH key issues before general permission denied
        elif (
            "key_load_public" in combined_lower
            and "invalid format" in combined_lower
        ):
            return (
                "SSH key format is invalid. Check that the SSH private key "
                "is properly formatted."
            )
        elif "no matching host key type found" in combined_lower:
            return (
                "SSH key type not supported by server. The server may not "
                "accept this SSH key algorithm."
            )
        elif "authentication failed" in combined_lower:
            return (
                "SSH authentication failed - check SSH key, username, and "
                "server configuration"
            )
        # Check for connection timeout/refused before "could not read" check
        elif (
            "connection timed out" in combined_lower
            or "connection refused" in combined_lower
        ):
            return (
                "Connection failed - check network connectivity and "
                "Gerrit server availability"
            )
        # Check for specific SSH publickey-only authentication failures
        elif "permission denied (publickey)" in combined_lower and not any(
            auth_method in combined_lower
            for auth_method in ["gssapi", "password", "keyboard"]
        ):
            return (
                "SSH public key authentication failed. The SSH key may be "
                "invalid, not authorized for this user, or the wrong key type."
            )
        # Check for general SSH permission issues
        elif "permission denied" in combined_lower:
            return "SSH permission denied - check SSH key and user permissions"
        elif "could not read from remote repository" in combined_lower:
            return (
                "Could not read from remote repository - check SSH "
                "authentication and repository access permissions"
            )
        # Check for Gerrit-specific issues
        elif "missing issue-id" in combined_lower:
            return "Missing Issue-ID in commit message."
        elif "commit not associated to any issue" in combined_lower:
            return "Commit not associated to any issue."
        elif (
            "remote rejected" in combined_lower
            and "refs/for/" in combined_lower
        ):
            # Extract specific rejection reason from output
            lines = combined_output.split("\n")
            for line in lines:
                if "! [remote rejected]" in line:
                    # Extract the reason in parentheses
                    if "(" in line and ")" in line:
                        reason = line[line.find("(") + 1 : line.find(")")]
                        return f"Gerrit rejected the push: {reason}"
                    return f"Gerrit rejected the push: {line.strip()}"
            return "Gerrit rejected the push for an unknown reason"
        else:
            return f"Unknown error: {exc}"

    def _query_gerrit_for_results(
        self,
        *,
        gerrit: GerritInfo,
        repo: RepoNames,
        change_ids: Sequence[str],
    ) -> SubmissionResult:
        """Query Gerrit for change URL/number and patchset sha via REST."""
        log.info("Querying Gerrit for submitted change(s) via REST")
        # Build Gerrit REST client (prefer HTTP basic auth if provided)
        base_path = os.getenv("GERRIT_HTTP_BASE_PATH", "").strip().strip("/")
        base_url = (
            f"https://{gerrit.host}/"
            if not base_path
            else f"https://{gerrit.host}/{base_path}/"
        )
        http_user = (
            os.getenv("GERRIT_HTTP_USER", "").strip()
            or os.getenv("GERRIT_SSH_USER_G2G", "").strip()
        )
        http_pass = os.getenv("GERRIT_HTTP_PASSWORD", "").strip()
        if GerritRestAPI is None:
            raise OrchestratorError(_MSG_PYGERRIT2_REQUIRED_REST)
        if http_user and http_pass:
            if HTTPBasicAuth is None:
                raise OrchestratorError(_MSG_PYGERRIT2_REQUIRED_AUTH)
            rest = GerritRestAPI(
                url=base_url, auth=HTTPBasicAuth(http_user, http_pass)
            )
        else:
            rest = GerritRestAPI(url=base_url)
        urls: list[str] = []
        nums: list[str] = []
        shas: list[str] = []
        for cid in change_ids:
            if not cid:
                continue
            # Limit results to 1, filter by project and open status,
            # include current revision
            query = f"limit:1 is:open project:{repo.project_gerrit} {cid}"
            path = f"/changes/?q={query}&o=CURRENT_REVISION&n=1"
            try:
                changes = rest.get(path)
            except Exception as exc:
                status = getattr(
                    getattr(exc, "response", None), "status_code", None
                )
                if not base_path and status == 404:
                    try:
                        fallback_url = f"https://{gerrit.host}/r/"
                        if GerritRestAPI is None:
                            log.warning(
                                "pygerrit2 missing; skipping REST fallback"
                            )
                            continue
                        if http_user and http_pass:
                            if HTTPBasicAuth is None:
                                log.warning(
                                    "pygerrit2 auth missing; skipping fallback"
                                )
                                continue
                            rest_fallback = GerritRestAPI(
                                url=fallback_url,
                                auth=HTTPBasicAuth(http_user, http_pass),
                            )
                        else:
                            rest_fallback = GerritRestAPI(url=fallback_url)
                        changes = rest_fallback.get(path)
                    except Exception as exc2:
                        log.warning(
                            "Failed to query change via REST for %s "
                            "(including '/r' fallback): %s",
                            cid,
                            exc2,
                        )
                        continue
                else:
                    log.warning(
                        "Failed to query change via REST for %s: %s", cid, exc
                    )
                    continue
            if not changes:
                continue
            change = changes[0]
            num = str(change.get("_number", ""))
            current_rev = change.get("current_revision", "")
            # Construct a stable web URL for the change
            if num:
                urls.append(
                    f"https://{gerrit.host}/c/{repo.project_gerrit}/+/{num}"
                )
                nums.append(num)
            if current_rev:
                shas.append(current_rev)
        # Export env variables (compat)
        if urls:
            os.environ["GERRIT_CHANGE_REQUEST_URL"] = "\n".join(urls)
        if nums:
            os.environ["GERRIT_CHANGE_REQUEST_NUM"] = "\n".join(nums)
        if shas:
            os.environ["GERRIT_COMMIT_SHA"] = "\n".join(shas)
        return SubmissionResult(
            change_urls=urls, change_numbers=nums, commit_shas=shas
        )

    def _setup_git_workspace(self, inputs: Inputs, gh: GitHubContext) -> None:
        """Initialize and set up git workspace for PR processing."""
        from .gitutils import run_cmd

        # Initialize git repository
        run_cmd(["git", "init"], cwd=self.workspace)

        # Add GitHub remote
        repo_full = gh.repository.strip() if gh.repository else ""
        server_url = gh.server_url or "https://github.com"
        server_url = server_url.rstrip("/")
        repo_url = f"{server_url}/{repo_full}.git"
        run_cmd(
            ["git", "remote", "add", "origin", repo_url],
            cwd=self.workspace,
        )

        # Fetch PR head
        if gh.pr_number:
            pr_ref = (
                f"refs/pull/{gh.pr_number}/head:"
                f"refs/remotes/origin/pr/{gh.pr_number}/head"
            )
            run_cmd(
                [
                    "git",
                    "fetch",
                    f"--depth={inputs.fetch_depth}",
                    "origin",
                    pr_ref,
                ],
                cwd=self.workspace,
            )
            # Checkout PR head
            pr_head_ref = f"refs/remotes/origin/pr/{gh.pr_number}/head"
            run_cmd(
                ["git", "checkout", "-B", "g2g_pr_head", pr_head_ref],
                cwd=self.workspace,
            )

    def _install_commit_msg_hook(self, gerrit: GerritInfo) -> None:
        """Manually install commit-msg hook from Gerrit."""
        from .gitutils import run_cmd

        hooks_dir = self.workspace / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        hook_path = hooks_dir / "commit-msg"

        # Download commit-msg hook using SSH
        try:
            # Use curl to download the hook (more reliable than scp)
            curl_cmd = [
                "curl",
                "-o",
                str(hook_path),
                f"https://{gerrit.host}/r/tools/hooks/commit-msg",
            ]
            run_cmd(curl_cmd, cwd=self.workspace)

            # Make hook executable
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
            log.debug("Successfully installed commit-msg hook via curl")

        except Exception as exc:
            log.warning("Failed to install commit-msg hook via curl: %s", exc)
            msg = f"Could not install commit-msg hook: {exc}"
            raise OrchestratorError(msg) from exc

    def _ensure_change_id_present(
        self, gerrit: GerritInfo, author: str
    ) -> list[str]:
        """Ensure the last commit has a Change-Id.

        Installs the commit-msg hook and amends the commit if needed.
        """
        trailers = git_last_commit_trailers(
            keys=["Change-Id"], cwd=self.workspace
        )
        if not trailers.get("Change-Id"):
            log.debug(
                "No Change-Id found, installing commit-msg hook and amending "
                "commit"
            )
            self._install_commit_msg_hook(gerrit)
            git_commit_amend(
                no_edit=True, signoff=True, author=author, cwd=self.workspace
            )
            # Debug: Check commit message after amend
            actual_msg = run_cmd(
                ["git", "show", "-s", "--pretty=format:%B", "HEAD"],
                cwd=self.workspace,
            ).stdout.strip()
            log.debug("Commit message after amend:\n%s", actual_msg)
            trailers = git_last_commit_trailers(
                keys=["Change-Id"], cwd=self.workspace
            )
        return [c for c in trailers.get("Change-Id", []) if c]

    def _add_backref_comment_in_gerrit(
        self,
        *,
        gerrit: GerritInfo,
        repo: RepoNames,
        branch: str,
        commit_shas: Sequence[str],
        gh: GitHubContext,
    ) -> None:
        """Post a comment in Gerrit pointing back to the GitHub PR and run."""
        if not commit_shas:
            log.warning("No commit shas to comment on in Gerrit")
            return

        # Check if back-reference comments are disabled
        if os.getenv("G2G_SKIP_GERRIT_COMMENTS", "").lower() in (
            "true",
            "1",
            "yes",
        ):
            log.info(
                "Skipping back-reference comments "
                "(G2G_SKIP_GERRIT_COMMENTS=true)"
            )
            return

        log.info("Adding back-reference comment in Gerrit")
        user = os.getenv("GERRIT_SSH_USER_G2G", "")
        server = gerrit.host
        pr_url = f"{gh.server_url}/{gh.repository}/pull/{gh.pr_number}"
        run_url = (
            f"{gh.server_url}/{gh.repository}/actions/runs/{gh.run_id}"
            if gh.run_id
            else "N/A"
        )
        message = f"GHPR: {pr_url} | Action-Run: {run_url}"
        log.info("Adding back-reference comment: %s", message)
        for csha in commit_shas:
            if not csha:
                continue
            try:
                log.debug("Executing SSH command for commit %s", csha)
                # Build SSH command with our configured SSH options
                ssh_cmd = ["ssh", "-n", "-p", str(gerrit.port)]

                # Add our SSH options if we have custom SSH config
                if self._git_ssh_command:
                    # Extract SSH options from GIT_SSH_COMMAND
                    # Format: "ssh -i /path/to/key -o Option=value ..."
                    git_ssh_parts = self._git_ssh_command.split()
                    if len(git_ssh_parts) > 1:  # Skip the "ssh" part
                        ssh_options = git_ssh_parts[1:]
                        log.debug("Adding SSH options: %s", ssh_options)
                        ssh_cmd.extend(ssh_options)
                else:
                    log.debug("No custom SSH config, using default SSH options")

                # Add the target and gerrit command
                ssh_cmd.extend(
                    [
                        f"{user}@{server}",
                        "gerrit",
                        "review",
                        "-m",
                        message,
                        "--branch",
                        branch,
                        "--project",
                        repo.project_gerrit,
                        csha,
                    ]
                )

                log.debug("Final SSH command: %s", " ".join(ssh_cmd))
                run_cmd(ssh_cmd, cwd=self.workspace)
                log.info(
                    "Successfully added back-reference comment for %s: %s",
                    csha,
                    message,
                )
            except CommandError as exc:
                log.warning(
                    "Failed to add back-reference comment for %s "
                    "(non-fatal): %s",
                    csha,
                    exc,
                )
                if exc.stderr:
                    log.debug("SSH stderr: %s", exc.stderr)
                if exc.stdout:
                    log.debug("SSH stdout: %s", exc.stdout)
                log.info(
                    "Back-reference comment failed but change was successfully "
                    "submitted. You can set G2G_SKIP_GERRIT_COMMENTS=true to "
                    "disable these comments."
                )
                # Continue processing - this is not a fatal error
            except Exception as exc:
                log.warning(
                    "Failed to add back-reference comment for %s "
                    "(non-fatal): %s",
                    csha,
                    exc,
                )
                log.debug(
                    "Back-reference comment failure details:", exc_info=True
                )
                # Continue processing - this is not a fatal error

    def _comment_on_pull_request(
        self,
        gh: GitHubContext,
        gerrit: GerritInfo,
        result: SubmissionResult,
    ) -> None:
        """Post a comment on the PR with the Gerrit change URL(s)."""
        log.info("Adding reference comment on PR #%s", gh.pr_number)
        if not gh.pr_number:
            return
        urls = result.change_urls or []
        org = os.getenv("ORGANIZATION", gh.repository_owner)
        text = (
            f"The pull-request PR-{gh.pr_number} is submitted to Gerrit "
            f"[{org}](https://{gerrit.host})!\n\n"
        )
        if urls:
            text += "To follow up on the change visit:\n\n" + "\n".join(urls)
        try:
            client = build_client()
            repo = get_repo_from_env(client)
            # At this point, gh.pr_number is non-None due to earlier guard.
            pr_obj = get_pull(repo, int(gh.pr_number))
            create_pr_comment(pr_obj, text)
        except Exception as exc:
            log.warning("Failed to add PR comment: %s", exc)

    def _close_pull_request_if_required(
        self,
        gh: GitHubContext,
    ) -> None:
        """Close the PR if policy requires (pull_request_target events).

        When PRESERVE_GITHUB_PRS is true, skip closing PRs (useful for testing).
        """
        # Respect PRESERVE_GITHUB_PRS to avoid closing PRs during tests
        preserve = os.getenv("PRESERVE_GITHUB_PRS", "").strip().lower()
        if preserve in ("1", "true", "yes"):
            log.info(
                "PRESERVE_GITHUB_PRS is enabled; skipping PR close for #%s",
                gh.pr_number,
            )
            return
        # The current shell action closes PR on pull_request_target events.
        if gh.event_name != "pull_request_target":
            log.debug("Event is not pull_request_target; not closing PR")
            return
        log.info("Closing PR #%s", gh.pr_number)
        try:
            client = build_client()
            repo = get_repo_from_env(client)
            pr_number = gh.pr_number
            if pr_number is None:
                return
            pr_obj = get_pull(repo, pr_number)
            close_pr(pr_obj, comment="Auto-closing pull request")
        except Exception as exc:
            log.warning("Failed to close PR #%s: %s", gh.pr_number, exc)

    def _dry_run_preflight(
        self,
        *,
        gerrit: GerritInfo,
        inputs: Inputs,
        gh: GitHubContext,
        repo: RepoNames,
    ) -> None:
        """Validate config, DNS, and credentials in dry-run mode.

        - Resolve Gerrit host via DNS
        - Verify SSH (TCP) reachability on the Gerrit port
        - Verify Gerrit REST endpoint is reachable; if credentials are provided,
          verify authentication by querying /accounts/self
        - Verify GitHub token by fetching repository and PR metadata
        - Do NOT perform any write operations
        """
        import socket

        log.info("Dry-run: starting preflight checks")
        if os.getenv("G2G_DRYRUN_DISABLE_NETWORK", "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            log.info(
                "Dry-run: network checks disabled (G2G_DRYRUN_DISABLE_NETWORK)"
            )
            log.info(
                "Dry-run targets: Gerrit project=%s branch=%s "
                "topic_prefix=GH-%s",
                repo.project_gerrit,
                self._resolve_target_branch(),
                repo.project_github,
            )
            if inputs.reviewers_email:
                log.info(
                    "Reviewers (from inputs/config): %s", inputs.reviewers_email
                )
            elif os.getenv("REVIEWERS_EMAIL"):
                log.info(
                    "Reviewers (from environment): %s",
                    os.getenv("REVIEWERS_EMAIL"),
                )
            return

        # DNS resolution for Gerrit host
        try:
            socket.getaddrinfo(gerrit.host, None)
            log.info(
                "DNS resolution for Gerrit host '%s' succeeded", gerrit.host
            )
        except Exception as exc:
            msg = "DNS resolution failed"
            raise OrchestratorError(msg) from exc

        # SSH (TCP) reachability on Gerrit port
        try:
            with socket.create_connection(
                (gerrit.host, gerrit.port), timeout=5
            ):
                pass
            log.info(
                "SSH TCP connectivity to %s:%s verified",
                gerrit.host,
                gerrit.port,
            )
        except Exception as exc:
            msg = "SSH TCP connectivity failed"
            raise OrchestratorError(msg) from exc

        # Gerrit REST reachability and optional auth check
        base_path = os.getenv("GERRIT_HTTP_BASE_PATH", "").strip().strip("/")
        http_user = (
            os.getenv("GERRIT_HTTP_USER", "").strip()
            or os.getenv("GERRIT_SSH_USER_G2G", "").strip()
        )
        http_pass = os.getenv("GERRIT_HTTP_PASSWORD", "").strip()
        self._verify_gerrit_rest(gerrit.host, base_path, http_user, http_pass)

        # GitHub token and metadata checks
        try:
            client = build_client()
            repo_obj = get_repo_from_env(client)
            if gh.pr_number is not None:
                pr_obj = get_pull(repo_obj, gh.pr_number)
                log.info(
                    "GitHub PR #%s metadata loaded successfully", gh.pr_number
                )
                try:
                    title, _ = get_pr_title_body(pr_obj)
                    log.info("GitHub PR title: %s", title)
                except Exception as exc:
                    log.debug("Failed to read PR title: %s", exc)
            else:
                # Enumerate at least one open PR to validate scope
                prs = list(iter_open_pulls(repo_obj))
                log.info(
                    "GitHub repository '%s' open PR count: %d",
                    gh.repository,
                    len(prs),
                )
        except Exception as exc:
            msg = "GitHub API validation failed"
            raise OrchestratorError(msg) from exc

        # Log effective targets
        log.info(
            "Dry-run targets: Gerrit project=%s branch=%s topic_prefix=GH-%s",
            repo.project_gerrit,
            self._resolve_target_branch(),
            repo.project_github,
        )
        if inputs.reviewers_email:
            log.info(
                "Reviewers (from inputs/config): %s", inputs.reviewers_email
            )
        elif os.getenv("REVIEWERS_EMAIL"):
            log.info(
                "Reviewers (from environment): %s", os.getenv("REVIEWERS_EMAIL")
            )

    def _verify_gerrit_rest(
        self,
        host: str,
        base_path: str,
        http_user: str,
        http_pass: str,
    ) -> None:
        """Probe Gerrit REST endpoint with optional auth and '/r' fallback."""

        def _build_client(url: str) -> Any:
            if http_user and http_pass:
                if GerritRestAPI is None:
                    raise OrchestratorError(_MSG_PYGERRIT2_MISSING)
                if HTTPBasicAuth is None:
                    raise OrchestratorError(_MSG_PYGERRIT2_AUTH_MISSING)
                return GerritRestAPI(
                    url=url, auth=HTTPBasicAuth(http_user, http_pass)
                )
            else:
                if GerritRestAPI is None:
                    raise OrchestratorError(_MSG_PYGERRIT2_MISSING)
                return GerritRestAPI(url=url)

        def _probe(url: str) -> None:
            rest: Any = _build_client(url)
            if http_user and http_pass:
                _ = rest.get("/accounts/self")
                log.info(
                    "Gerrit REST authenticated access verified for user '%s'",
                    http_user,
                )
            else:
                _ = rest.get("/dashboard/self")
                log.info("Gerrit REST endpoint reachable (unauthenticated)")

        base_url = (
            f"https://{host}/"
            if not base_path
            else f"https://{host}/{base_path}/"
        )
        try:
            _probe(base_url)
        except Exception as exc:
            status = getattr(
                getattr(exc, "response", None), "status_code", None
            )
            if not base_path and status == 404:
                try:
                    fallback_url = f"https://{host}/r/"
                    _probe(fallback_url)
                except Exception as exc2:
                    log.warning(
                        "Gerrit REST probe did not succeed "
                        "(including '/r' fallback): %s",
                        exc2,
                    )
            else:
                log.warning("Gerrit REST probe did not succeed: %s", exc)

    # ---------------
    # Helpers
    # ---------------

    def _append_github_output(self, outputs: dict[str, str]) -> None:
        gh_out = os.getenv("GITHUB_OUTPUT")
        if not gh_out:
            return
        try:
            with open(gh_out, "a", encoding="utf-8") as fh:
                for key, val in outputs.items():
                    if not val:
                        continue
                    if "\n" in val and os.getenv("GITHUB_ACTIONS") == "true":
                        fh.write(f"{key}<<G2G\n")
                        fh.write(f"{val}\n")
                        fh.write("G2G\n")
                    else:
                        fh.write(f"{key}={val}\n")
        except Exception as exc:
            log.debug("Failed to write GITHUB_OUTPUT: %s", exc)

    def _resolve_target_branch(self) -> str:
        # Preference order:
        # 1) GERRIT_BRANCH (explicit override)
        # 2) GITHUB_BASE_REF (provided in Actions PR context)
        # 3) origin/HEAD default (if available)
        # 4) 'main' as a common default
        # 5) 'master' as a legacy default
        b = os.getenv("GERRIT_BRANCH", "").strip()
        if b:
            return b
        b = os.getenv("GITHUB_BASE_REF", "").strip()
        if b:
            return b
        # Try resolve origin/HEAD -> origin/<branch>
        try:
            from .gitutils import git_quiet

            res = git_quiet(
                ["rev-parse", "--abbrev-ref", "origin/HEAD"],
                cwd=self.workspace,
            )
            if res.returncode == 0:
                name = (res.stdout or "").strip()
                branch = name.split("/", 1)[1] if "/" in name else name
                if branch:
                    return branch
        except Exception as exc:
            log.debug("origin/HEAD probe failed: %s", exc)
        # Prefer 'master' when present
        try:
            from .gitutils import git_quiet

            res3 = git_quiet(
                ["show-ref", "--verify", "refs/remotes/origin/master"],
                cwd=self.workspace,
            )
            if res3.returncode == 0:
                return "master"
        except Exception as exc:
            log.debug("origin/master probe failed: %s", exc)
        # Fall back to 'main' if present
        try:
            from .gitutils import git_quiet

            res2 = git_quiet(
                ["show-ref", "--verify", "refs/remotes/origin/main"],
                cwd=self.workspace,
            )
            if res2.returncode == 0:
                return "main"
        except Exception as exc:
            log.debug("origin/main probe failed: %s", exc)
        return "master"

    def _resolve_reviewers(self, inputs: Inputs) -> str:
        # If empty, use the Gerrit SSH user's email as default.
        if inputs.reviewers_email.strip():
            return inputs.reviewers_email.strip()
        return inputs.gerrit_ssh_user_g2g_email.strip()

    def _get_last_change_ids_from_head(self) -> list[str]:
        """Return Change-Id trailer(s) from HEAD commit, if present."""
        try:
            trailers = git_last_commit_trailers(keys=["Change-Id"])
        except GitError:
            return []
        values = trailers.get("Change-Id", [])
        return [v for v in values if v]

    def _validate_change_ids(self, ids: Iterable[str]) -> list[str]:
        """Basic validation for Change-Id strings."""
        out: list[str] = []
        for cid in ids:
            c = cid.strip()
            if not c:
                continue
            if not _is_valid_change_id(c):
                log.debug("Ignoring invalid Change-Id: %s", c)
                continue
            out.append(c)
        return out


# ---------------------
# Utility functions
# ---------------------

# moved _is_valid_change_id above its first use
