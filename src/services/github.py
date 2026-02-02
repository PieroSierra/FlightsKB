"""GitHub Contents API client for FlightsKB knowledge management."""

import base64
import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class GitHubConfig:
    """Configuration for GitHub API integration."""

    owner: str
    repo: str
    token: str
    branch: str = "main"
    base_url: str = "https://api.github.com"


@dataclass
class GitHubFile:
    """Represents a file retrieved from or written to GitHub."""

    path: str
    content: str
    sha: str
    name: str = ""
    type: str = "file"


@dataclass
class GitHubCommitResult:
    """Result of a create/update file operation."""

    commit_sha: str
    commit_url: str
    file_path: str
    file_sha: str


class GitHubContentsClient:
    """Async client for GitHub Contents API."""

    def __init__(self, config: GitHubConfig):
        """
        Initialize the GitHub client.

        Args:
            config: GitHub configuration with owner, repo, token, etc.
        """
        self.config = config
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {config.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _url(self, path: str) -> str:
        """Build API URL for a file path."""
        return f"{self.config.base_url}/repos/{self.config.owner}/{self.config.repo}/contents/{path}"

    async def read_file(
        self,
        path: str,
        ref: Optional[str] = None,
    ) -> GitHubFile:
        """
        Read a file from the repository.

        Args:
            path: File path relative to repo root.
            ref: Branch/tag/commit (defaults to config branch).

        Returns:
            GitHubFile with decoded content and SHA.

        Raises:
            httpx.HTTPStatusError: On API errors (404, 403, etc.)
        """
        params = {"ref": ref or self.config.branch}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._url(path),
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if data.get("type") != "file":
                raise ValueError(f"Path {path} is not a file (type: {data.get('type')})")

            content = base64.b64decode(data["content"]).decode("utf-8")
            return GitHubFile(
                path=data["path"],
                content=content,
                sha=data["sha"],
                name=data["name"],
                type="file",
            )

    async def list_directory(
        self,
        path: str = "",
        ref: Optional[str] = None,
    ) -> list[dict]:
        """
        List contents of a directory.

        Args:
            path: Directory path relative to repo root.
            ref: Branch/tag/commit (defaults to config branch).

        Returns:
            List of file/directory metadata dicts with keys:
            - type: "file" or "dir"
            - name: filename
            - path: full path
            - sha: blob SHA
        """
        params = {"ref": ref or self.config.branch}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._url(path),
                headers=self.headers,
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()

            return response.json()

    async def list_markdown_files_recursive(
        self,
        path: str = "knowledge",
    ) -> list[str]:
        """
        Recursively list all Markdown files under a path.

        Args:
            path: Starting directory path.

        Returns:
            List of file paths (e.g., ["knowledge/airlines/BA/overview.md", ...])
        """
        md_files: list[str] = []

        async def _recurse(dir_path: str) -> None:
            try:
                items = await self.list_directory(dir_path)

                for item in items:
                    if item["type"] == "file" and item["name"].endswith(".md"):
                        md_files.append(item["path"])
                    elif item["type"] == "dir":
                        await _recurse(item["path"])
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Directory doesn't exist, skip
                    pass
                else:
                    raise

        await _recurse(path)
        return md_files

    async def create_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
    ) -> GitHubCommitResult:
        """
        Create a new file in the repository.

        Args:
            path: File path (e.g., "knowledge/inbox/new-article.md")
            content: File content (plain text, will be base64 encoded)
            message: Commit message
            branch: Target branch (defaults to config branch)

        Returns:
            GitHubCommitResult with commit info

        Raises:
            httpx.HTTPStatusError: 422 if file already exists
        """
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")

        payload = {
            "message": message,
            "content": encoded_content,
            "branch": branch or self.config.branch,
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                self._url(path),
                headers=self.headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()
            return GitHubCommitResult(
                commit_sha=data["commit"]["sha"],
                commit_url=data["commit"]["html_url"],
                file_path=data["content"]["path"],
                file_sha=data["content"]["sha"],
            )

    async def get_rate_limit(self) -> dict:
        """
        Get current rate limit status.

        Returns:
            Dict with limit, remaining, and reset timestamp.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.config.base_url}/rate_limit",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()

            data = response.json()
            core = data.get("resources", {}).get("core", {})
            return {
                "limit": core.get("limit", 0),
                "remaining": core.get("remaining", 0),
                "reset": core.get("reset", 0),
            }


class GitHubConfigurationError(Exception):
    """Raised when GitHub integration is not properly configured."""

    pass


def get_github_client() -> Optional[GitHubContentsClient]:
    """
    Factory function to create a GitHub client from environment variables.

    Returns:
        GitHubContentsClient if configured, None otherwise.

    Environment variables:
        GITHUB_TOKEN: Fine-grained PAT with Contents read/write
        GITHUB_OWNER: Repository owner (username or org)
        GITHUB_REPO: Repository name
        GITHUB_BRANCH: Target branch (default: main)
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    owner = os.environ.get("GITHUB_OWNER", "").strip()
    repo = os.environ.get("GITHUB_REPO", "").strip()
    branch = os.environ.get("GITHUB_BRANCH", "main").strip()

    # Check for empty or placeholder values
    if not token or not owner or not repo:
        return None

    # Check for common placeholder patterns
    placeholder_patterns = ["xxx", "your-", "placeholder", "change-me"]
    for pattern in placeholder_patterns:
        if pattern in token.lower() or pattern in owner.lower() or pattern in repo.lower():
            return None

    config = GitHubConfig(
        owner=owner,
        repo=repo,
        token=token,
        branch=branch,
    )

    return GitHubContentsClient(config)


def get_github_client_or_raise() -> GitHubContentsClient:
    """
    Get GitHub client or raise an error if not configured.

    Returns:
        GitHubContentsClient

    Raises:
        GitHubConfigurationError: If required env vars are missing.
    """
    client = get_github_client()
    if client is None:
        missing = []
        if not os.environ.get("GITHUB_TOKEN"):
            missing.append("GITHUB_TOKEN")
        if not os.environ.get("GITHUB_OWNER"):
            missing.append("GITHUB_OWNER")
        if not os.environ.get("GITHUB_REPO"):
            missing.append("GITHUB_REPO")
        raise GitHubConfigurationError(
            f"GitHub integration not configured. Missing: {', '.join(missing)}"
        )
    return client
