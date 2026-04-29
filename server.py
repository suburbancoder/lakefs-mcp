"""lakeFS MCP Server — exposes lakeFS operations as MCP tools."""

import mimetypes
import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

LAKEFS_ENDPOINT = os.environ.get("LAKEFS_ENDPOINT", "http://localhost:8080")
LAKEFS_ACCESS_KEY = os.environ.get("LAKEFS_ACCESS_KEY_ID", "")
LAKEFS_SECRET_KEY = os.environ.get("LAKEFS_SECRET_ACCESS_KEY", "")

mcp = FastMCP("lakefs")


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=f"{LAKEFS_ENDPOINT}/api/v1",
        auth=(LAKEFS_ACCESS_KEY, LAKEFS_SECRET_KEY),
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

@mcp.tool()
def list_repositories(prefix: str = "", after: str = "", amount: int = 100) -> dict:
    """List all lakeFS repositories the configured user can access."""
    with _client() as client:
        resp = client.get("/repositories", params={"prefix": prefix, "after": after, "amount": amount})
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def get_repository(repository: str) -> dict:
    """Get details for a specific lakeFS repository."""
    with _client() as client:
        resp = client.get(f"/repositories/{repository}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def create_repository(
    name: str,
    storage_namespace: str,
    default_branch: str = "main",
    sample_data: bool = False,
) -> dict:
    """Create a new lakeFS repository.

    Args:
        name: Repository name.
        storage_namespace: Underlying storage URI (e.g. s3://my-bucket/prefix).
        default_branch: Name of the default branch (default: main).
        sample_data: Populate the repository with sample data.
    """
    with _client() as client:
        resp = client.post(
            "/repositories",
            json={
                "name": name,
                "storage_namespace": storage_namespace,
                "default_branch": default_branch,
                "sample_data": sample_data,
            },
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def delete_repository(repository: str) -> str:
    """Delete a lakeFS repository. This is irreversible.

    Args:
        repository: Repository name.
    """
    with _client() as client:
        resp = client.delete(f"/repositories/{repository}")
        resp.raise_for_status()
        return f"Repository '{repository}' deleted."


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

@mcp.tool()
def list_branches(repository: str, prefix: str = "", after: str = "", amount: int = 100) -> dict:
    """List branches in a lakeFS repository.

    Args:
        repository: Repository name.
        prefix: Filter branches by name prefix.
        after: Pagination cursor.
        amount: Maximum number of results.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/branches",
            params={"prefix": prefix, "after": after, "amount": amount},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def get_branch(repository: str, branch: str) -> dict:
    """Get details for a specific branch.

    Args:
        repository: Repository name.
        branch: Branch name.
    """
    with _client() as client:
        resp = client.get(f"/repositories/{repository}/branches/{branch}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def create_branch(repository: str, name: str, source: str) -> str:
    """Create a new branch in a lakeFS repository.

    Args:
        repository: Repository name.
        name: New branch name.
        source: Source branch or commit ID to branch from.
    """
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/branches",
            json={"name": name, "source": source},
        )
        resp.raise_for_status()
        return resp.text or f"Branch '{name}' created from '{source}'."


@mcp.tool()
def delete_branch(repository: str, branch: str) -> str:
    """Delete a branch from a lakeFS repository.

    Args:
        repository: Repository name.
        branch: Branch name to delete.
    """
    with _client() as client:
        resp = client.delete(f"/repositories/{repository}/branches/{branch}")
        resp.raise_for_status()
        return f"Branch '{branch}' deleted from '{repository}'."


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@mcp.tool()
def list_tags(repository: str, prefix: str = "", after: str = "", amount: int = 100) -> dict:
    """List tags in a lakeFS repository.

    Args:
        repository: Repository name.
        prefix: Filter tags by name prefix.
        after: Pagination cursor.
        amount: Maximum number of results.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/tags",
            params={"prefix": prefix, "after": after, "amount": amount},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def create_tag(repository: str, tag: str, ref: str) -> dict:
    """Create a tag pointing to a commit or ref.

    Args:
        repository: Repository name.
        tag: Tag name.
        ref: Commit ID or branch name to tag.
    """
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/tags",
            json={"id": tag, "ref": ref},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def delete_tag(repository: str, tag: str) -> str:
    """Delete a tag from a lakeFS repository.

    Args:
        repository: Repository name.
        tag: Tag name to delete.
    """
    with _client() as client:
        resp = client.delete(f"/repositories/{repository}/tags/{tag}")
        resp.raise_for_status()
        return f"Tag '{tag}' deleted from '{repository}'."


# ---------------------------------------------------------------------------
# Commits
# ---------------------------------------------------------------------------

@mcp.tool()
def log_commits(
    repository: str,
    ref: str,
    after: str = "",
    amount: int = 100,
    objects: list[str] | None = None,
    prefixes: list[str] | None = None,
) -> dict:
    """Get commit log for a branch or ref.

    Args:
        repository: Repository name.
        ref: Branch name or commit ID.
        after: Pagination cursor (commit ID).
        amount: Maximum number of commits to return.
        objects: Filter commits that touched these exact object paths.
        prefixes: Filter commits that touched objects under these prefixes.
    """
    params: dict = {"after": after, "amount": amount}
    if objects:
        params["objects"] = objects
    if prefixes:
        params["prefixes"] = prefixes
    with _client() as client:
        resp = client.get(f"/repositories/{repository}/commits", params={"ref": ref, **params})
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def get_commit(repository: str, commit_id: str) -> dict:
    """Get details for a specific commit.

    Args:
        repository: Repository name.
        commit_id: Commit SHA.
    """
    with _client() as client:
        resp = client.get(f"/repositories/{repository}/commits/{commit_id}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def commit(
    repository: str,
    branch: str,
    message: str,
    metadata: dict | None = None,
    allow_empty: bool = False,
) -> dict:
    """Commit staged changes on a branch.

    Args:
        repository: Repository name.
        branch: Branch name with staged changes.
        message: Commit message.
        metadata: Optional key-value metadata to attach.
        allow_empty: Allow committing even if there are no changes.
    """
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/branches/{branch}/commits",
            json={
                "message": message,
                "metadata": metadata or {},
                "allow_empty": allow_empty,
            },
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Objects
# ---------------------------------------------------------------------------

@mcp.tool()
def list_objects(
    repository: str,
    ref: str,
    prefix: str = "",
    after: str = "",
    amount: int = 100,
    delimiter: str = "/",
    user_metadata: bool = False,
) -> dict:
    """List objects (files) in a lakeFS repository at a given ref.

    Args:
        repository: Repository name.
        ref: Branch name, tag, or commit ID.
        prefix: Filter objects by path prefix.
        after: Pagination cursor.
        amount: Maximum number of objects to return.
        delimiter: Delimiter for hierarchical listing (use '/' for directory-like view).
        user_metadata: Include user-defined metadata in results.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/refs/{ref}/objects/ls",
            params={
                "prefix": prefix,
                "after": after,
                "amount": amount,
                "delimiter": delimiter,
                "user_metadata": user_metadata,
            },
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def stat_object(repository: str, ref: str, path: str, user_metadata: bool = True) -> dict:
    """Get metadata/stats for a specific object.

    Args:
        repository: Repository name.
        ref: Branch name, tag, or commit ID.
        path: Object path within the repository.
        user_metadata: Include user-defined metadata.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/refs/{ref}/objects/stat",
            params={"path": path, "user_metadata": user_metadata},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def delete_object(repository: str, branch: str, path: str) -> str:
    """Delete an object from a branch (staged for commit).

    Args:
        repository: Repository name.
        branch: Branch name.
        path: Object path to delete.
    """
    with _client() as client:
        resp = client.delete(
            f"/repositories/{repository}/branches/{branch}/objects",
            params={"path": path},
        )
        resp.raise_for_status()
        return f"Object '{path}' deleted from branch '{branch}'."


@mcp.tool()
def upload_object(
    repository: str,
    branch: str,
    local_path: str,
    dest_path: str = "",
    create_branch_if_missing: bool = False,
) -> dict:
    """Upload a local file to a lakeFS branch (staged for commit).

    A branch name is always required. Writing directly to 'main' is not
    allowed by lakeFS — use a feature branch and merge when ready.

    If the branch does not exist and create_branch_if_missing is False (the
    default), the tool returns a prompt asking the user to confirm creation.
    Set create_branch_if_missing=True to create the branch automatically from
    main without asking.

    Args:
        repository: Repository name.
        branch: Branch name to upload to. Must not be 'main'.
        local_path: Path to the local file. Accepts absolute paths, relative
                    paths, or just a filename (e.g. 'test.txt',
                    'data/file.csv', '/Users/me/data/file.parquet').
        dest_path: Destination path inside the repository. Defaults to the
                   file's basename.
        create_branch_if_missing: When True, create the branch from main
                                  automatically if it does not exist.
    """
    if branch == "main":
        raise ValueError(
            "Direct uploads to 'main' are not allowed. Please specify a feature branch. "
            "If it doesn't exist yet, re-run with create_branch_if_missing=True."
        )

    local_path = os.path.expanduser(local_path)
    if not os.path.isabs(local_path):
        local_path = os.path.join(os.getcwd(), local_path)

    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"No file found at: {local_path}")

    if not dest_path:
        dest_path = os.path.basename(local_path)

    with _client() as client:
        # Check whether the branch exists
        branch_resp = client.get(f"/repositories/{repository}/branches/{branch}")
        if branch_resp.status_code == 404:
            if not create_branch_if_missing:
                return {
                    "status": "branch_missing",
                    "message": (
                        f"Branch '{branch}' does not exist in '{repository}'. "
                        f"Would you like to create it from 'main' and proceed with the upload?"
                    ),
                }
            # Create from main
            create_resp = client.post(
                f"/repositories/{repository}/branches",
                json={"name": branch, "source": "main"},
            )
            create_resp.raise_for_status()

        content_type, _ = mimetypes.guess_type(local_path)
        content_type = content_type or "application/octet-stream"

        with open(local_path, "rb") as f:
            data = f.read()

        resp = client.post(
            f"/repositories/{repository}/branches/{branch}/objects",
            params={"path": dest_path},
            content=data,
            headers={"Content-Type": content_type},
        )
        resp.raise_for_status()
        return {"dest_path": dest_path, "size_bytes": len(data), "content_type": content_type}


# ---------------------------------------------------------------------------
# Diff & Changes
# ---------------------------------------------------------------------------

@mcp.tool()
def diff_refs(
    repository: str,
    left_ref: str,
    right_ref: str,
    prefix: str = "",
    after: str = "",
    amount: int = 100,
    delimiter: str = "/",
) -> dict:
    """Show the diff between two refs (branches, tags, or commits).

    Args:
        repository: Repository name.
        left_ref: Left side ref (branch/tag/commit).
        right_ref: Right side ref (branch/tag/commit).
        prefix: Limit diff to objects under this prefix.
        after: Pagination cursor.
        amount: Maximum number of diff entries to return.
        delimiter: Delimiter for path grouping.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/refs/{left_ref}/diff/{right_ref}",
            params={"prefix": prefix, "after": after, "amount": amount, "delimiter": delimiter},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def uncommitted_changes(
    repository: str,
    branch: str,
    prefix: str = "",
    after: str = "",
    amount: int = 100,
) -> dict:
    """Show uncommitted (staged) changes on a branch.

    Args:
        repository: Repository name.
        branch: Branch name.
        prefix: Limit to objects under this prefix.
        after: Pagination cursor.
        amount: Maximum number of entries to return.
    """
    with _client() as client:
        resp = client.get(
            f"/repositories/{repository}/branches/{branch}/diff",
            params={"prefix": prefix, "after": after, "amount": amount},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Merge & Revert
# ---------------------------------------------------------------------------

@mcp.tool()
def merge_into_branch(
    repository: str,
    source_branch: str,
    destination_branch: str,
    message: str = "",
    metadata: dict | None = None,
    strategy: str = "",
) -> dict:
    """Merge source_branch into destination_branch.

    Args:
        repository: Repository name.
        source_branch: Branch to merge from.
        destination_branch: Branch to merge into.
        message: Optional merge commit message.
        metadata: Optional key-value metadata for the merge commit.
        strategy: Merge strategy — 'none', 'source-wins', or 'dest-wins'.
    """
    body: dict = {}
    if message:
        body["message"] = message
    if metadata:
        body["metadata"] = metadata
    if strategy:
        body["strategy"] = strategy
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/refs/{source_branch}/merge/{destination_branch}",
            json=body,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def revert_branch(
    repository: str,
    branch: str,
    ref: str,
    parent_number: int = 1,
) -> str:
    """Revert a commit on a branch (creates a new revert commit).

    Args:
        repository: Repository name.
        branch: Branch to revert on.
        ref: Commit ID or ref to revert.
        parent_number: For merge commits, which parent to revert to (1-based).
    """
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/branches/{branch}/revert",
            json={"ref": ref, "parent_number": parent_number},
        )
        resp.raise_for_status()
        return f"Reverted '{ref}' on branch '{branch}'."


@mcp.tool()
def cherry_pick(repository: str, branch: str, ref: str, parent_number: int = 1) -> dict:
    """Cherry-pick a commit onto a branch.

    Args:
        repository: Repository name.
        branch: Target branch.
        ref: Commit ID to cherry-pick.
        parent_number: For merge commits, which parent to diff against (1-based).
    """
    with _client() as client:
        resp = client.post(
            f"/repositories/{repository}/branches/{branch}/cherry-pick",
            json={"ref": ref, "parent_number": parent_number},
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Actions / Hooks
# ---------------------------------------------------------------------------

@mcp.tool()
def list_action_runs(
    repository: str,
    branch: str = "",
    commit: str = "",
    after: str = "",
    amount: int = 100,
) -> dict:
    """List action (hook) runs for a repository.

    Args:
        repository: Repository name.
        branch: Filter by branch name.
        commit: Filter by commit ID.
        after: Pagination cursor.
        amount: Maximum number of results.
    """
    params: dict = {"after": after, "amount": amount}
    if branch:
        params["branch"] = branch
    if commit:
        params["commit"] = commit
    with _client() as client:
        resp = client.get(f"/repositories/{repository}/actions/runs", params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def get_action_run(repository: str, run_id: str) -> dict:
    """Get details for a specific action run.

    Args:
        repository: Repository name.
        run_id: Action run ID.
    """
    with _client() as client:
        resp = client.get(f"/repositories/{repository}/actions/runs/{run_id}")
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

@mcp.tool()
def get_config() -> dict:
    """Retrieve the lakeFS server configuration."""
    with _client() as client:
        resp = client.get("/config")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def whoami() -> dict:
    """Return the currently authenticated lakeFS user."""
    with _client() as client:
        resp = client.get("/user")
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    mcp.run()
