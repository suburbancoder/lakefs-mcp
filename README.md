# lakefs-mcp

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes [lakeFS](https://github.com/treeverse/lakeFS) operations as tools for AI assistants like Claude.

## Tools

| Group | Tools |
|---|---|
| **Repositories** | `list_repositories`, `get_repository`, `create_repository`, `delete_repository` |
| **Branches** | `list_branches`, `get_branch`, `create_branch`, `delete_branch` |
| **Tags** | `list_tags`, `create_tag`, `delete_tag` |
| **Commits** | `log_commits`, `get_commit`, `commit` |
| **Objects** | `list_objects`, `stat_object`, `delete_object` |
| **Diff** | `diff_refs`, `uncommitted_changes` |
| **Merge / Revert** | `merge_into_branch`, `revert_branch`, `cherry_pick` |
| **Actions** | `list_action_runs`, `get_action_run` |
| **System** | `get_config`, `whoami` |

## Requirements

- Python 3.11+
- A running lakeFS instance

## Setup

```bash
git clone https://github.com/suburbancoder/lakefs-mcp.git
cd lakefs-mcp

python3 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]" httpx

cp .env.example .env
# Edit .env with your lakeFS credentials
```

## Configuration

Set the following environment variables (or copy `.env.example` to `.env`):

| Variable | Default | Description |
|---|---|---|
| `LAKEFS_ENDPOINT` | `http://localhost:8080` | lakeFS server URL |
| `LAKEFS_ACCESS_KEY_ID` | — | lakeFS access key |
| `LAKEFS_SECRET_ACCESS_KEY` | — | lakeFS secret key |

## Running

```bash
source .venv/bin/activate
export LAKEFS_ENDPOINT=http://localhost:8080
export LAKEFS_ACCESS_KEY_ID=your-access-key
export LAKEFS_SECRET_ACCESS_KEY=your-secret-key

python server.py
```

## Connecting to Claude Code

The server loads credentials directly from its `.env` file at startup, so you don't need to pass them to the CLI command. Just register the binary and script paths:

```bash
claude mcp add lakefs \
  --scope user \
  /path/to/lakefs-mcp/.venv/bin/python \
  /path/to/lakefs-mcp/server.py
```

`--scope user` makes the server available in all your projects. Use `--scope local` to limit it to the current project.

Verify with:

```bash
claude mcp get lakefs
```

## License

MIT
