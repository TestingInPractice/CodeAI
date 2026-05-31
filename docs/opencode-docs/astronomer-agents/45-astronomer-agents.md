# Astronomer/agents — AI Agent Tooling for Data Engineering Workflows

## Overview

**Repo:** [astronomer/agents](https://github.com/astronomer/agents) (376 ★, Apache 2.0)  
**By:** [Astronomer](https://www.astronomer.io/) — the company behind Apache Airflow  
**What it is:** A complete AI agent toolkit for data engineering — MCP server for Airflow, 26 skills, CLI tool, and plugin system for Claude Code / Cursor / any MCP client.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              astronomer/agents                   │
├───────────────────┬─────────────────────────────┤
│  astro-airflow-mcp │          skills/            │
│  (MCP Server)      │   ┌─────────────────────┐  │
│                    │   │  warehouse-init     │  │
│  ┌──────────────┐  │   │  analyzing-data     │  │
│  │ AirflowV2    │  │   │  profiling-tables   │  │
│  │ Adapter      │  │   │  checking-freshness │  │
│  ├──────────────┤  │   │  authoring-dags     │  │
│  │ AirflowV3    │  │   │  testing-dags       │  │
│  │ Adapter      │  │   │  debugging-dags     │  │
│  └──────────────┘  │   │  deploying-airflow  │  │
│                    │   │  tracing-lineage    │  │
│  af CLI (built-in) │   │  cosmos-dbt-core    │  │
│                    │   │  migrating-2-to-3   │  │
│                    │   │  ... (26 total)     │  │
└───────────────────┴─────────────────────────────┘
```

## Key Components

### 1. Airflow MCP Server (`astro-airflow-mcp`)

Published on PyPI — run with `uvx` (no install needed):

```bash
uvx astro-airflow-mcp --transport stdio
```

**Architecture:** Built with [FastMCP](https://github.com/jlowin/fastmcp), adapter pattern for Airflow 2.x and 3.x version compatibility:
- `AirflowV2Adapter` — `/api/v1` REST API, basic auth
- `AirflowV3Adapter` — `/api/v2` REST API, OAuth2 token exchange
- Version auto-detection at startup by probing API endpoints
- Minor-version feature detection with graceful fallbacks

**93+ MCP Tools:**

| Category | Tools |
|----------|-------|
| **Consolidated** | `explore_dag`, `diagnose_dag_run`, `get_system_health` |
| **DAG Operations** | `list_dags`, `get_dag_details`, `get_dag_source`, `get_dag_stats`, `list_dag_warnings`, `list_import_errors`, `pause_dag`, `unpause_dag` |
| **Run Operations** | `list_dag_runs`, `get_dag_run`, `trigger_dag`, `trigger_dag_and_wait`, `delete_dag_run`, `clear_dag_run` |
| **Task Operations** | `list_tasks`, `get_task`, `get_task_instance`, `get_task_logs`, `clear_task_instances` |
| **Config** | `list_pools`, `get_pool`, `list_variables`, `get_variable`, `list_connections`, `list_assets`, `list_asset_events`, `get_upstream_asset_events`, `list_plugins`, `list_providers`, `get_airflow_config`, `get_airflow_version` |

**Deployment modes:**
1. **Standalone** — independent ASGI server (stdio or HTTP)
2. **Airflow Plugin** — mount directly into Airflow's webserver (FastAPI on AF3, Flask blueprint on AF2 via asyncio bridge)
3. **AF CLI** — `af` command-line tool with instance management

### 2. `af` CLI Tool

Built into `astro-airflow-mcp`, provides terminal access to everything:

```bash
uvx --from astro-airflow-mcp af --help

# Instance management (git-config-style scoping)
af instance add prod --url https://airflow.example.com --token "$TOKEN"
af instance use prod
af instance discover           # Auto-find Astro + local instances

# DAG ops
af dags list
af dags explore <dag_id>       # Full investigation: metadata + tasks + source
af runs diagnose <dag_id> <run_id>

# Provider Registry (no Airflow instance needed)
af registry providers
af registry modules amazon
af registry parameters ftp

# Direct REST API access
af api ls
af api dags -F limit=10
```

**Config scoping** (mirrors `git config`):

| Scope | File | Committed? |
|-------|------|------------|
| Global | `~/.astro/config.yaml` | n/a (per-user) |
| Project shared | `<root>/.astro/config.yaml` | yes |
| Project local | `<root>/.astro/config.local.yaml` | no (gitignored) |

Supports environment variable interpolation (`${VAR}`) in config files.

### 3. Skills (26 total)

Skills are Markdown files with YAML frontmatter in `skills/<name>/SKILL.md`. Claude auto-invokes them based on description matching.

#### Data Discovery & Analysis

| Skill | Description |
|-------|-------------|
| `warehouse-init` | Generate `.astro/warehouse.md` with full schema metadata |
| `analyzing-data` | SQL-based analysis via background Jupyter kernel |
| `checking-freshness` | Check how current your data is |
| `profiling-tables` | Table profiling and quality assessment |

#### Data Lineage

| Skill | Description |
|-------|-------------|
| `tracing-downstream-lineage` | Impact analysis — what breaks if you change something |
| `tracing-upstream-lineage` | Trace where data comes from |
| `annotating-task-lineage` | Add manual lineage via inlets/outlets |
| `creating-openlineage-extractors` | Build custom OpenLineage extractors |

#### DAG Development

| Skill | Description |
|-------|-------------|
| `airflow` (entrypoint) | Routes to sub-skills, covers all `af` CLI commands |
| `setting-up-astro-project` | Initialize new Astro/Airflow projects |
| `managing-astro-local-env` | Start/stop/logs/troubleshoot local Airflow |
| `authoring-dags` | Create DAGs with best practices (6-phase workflow: Discover → Plan → Implement → Validate → Test → Iterate) |
| `blueprint` | Compose DAGs from YAML with Pydantic validation |
| `testing-dags` | Test/debug/fix/retest loop |
| `debugging-dags` | Deep failure diagnosis and root cause analysis |
| `deploying-airflow` | Deploy to Astro, Docker Compose, Kubernetes |
| `airflow-hitl` | Human-in-the-loop: approval gates, form input (AF 3.1+) |

#### dbt Integration

| Skill | Description |
|-------|-------------|
| `cosmos-dbt-core` | Run dbt Core as Airflow DAGs via Astronomer Cosmos |
| `cosmos-dbt-fusion` | dbt Fusion with Snowflake/Databricks |

#### Migration

| Skill | Description |
|-------|-------------|
| `migrating-airflow-2-to-3` | Migrate DAGs from AF 2.x to 3.x |

## Plugin Structure

### Claude Code Plugin (`.claude-plugin/`)

```
.claude-plugin/
├── marketplace.json     # Catalog entry (strict: false)
└── plugin.json          # Manifest with hooks

skills/
└── <name>/
    ├── SKILL.md         # YAML frontmatter + instructions
    └── hooks/           # Co-located hook scripts
        └── *.sh
```

**Install:**
```bash
claude plugin marketplace add astronomer/agents
claude plugin install astronomer-data@astronomer
```

**Key detail:** `marketplace.json` uses `"strict": false` — this means the plugin is loaded verbatim from the repo without requiring a strict schema. Skills use `${CLAUDE_PLUGIN_ROOT}` to reference files within the plugin (required because plugins are copied to a cache location when installed). However, hooks in `SKILL.md` frontmatter can use **relative paths** from the skill's directory.

**Hooks** (from `plugin.json`):
- `SessionStart` — async warm `uvx` cache for faster first invocation
- `Stop` — clean up Jupyter kernel for `analyzing-data` skill

### Cursor Plugin (`.cursor-plugin/`)

```
.cursor-plugin/
└── plugin.json          # Same metadata, Cursor-compatible hooks
```

Cursor supports both MCP servers (via `mcp.json`) and skills (via `npx skills add`).

## Warehouse Integration

### Connection Configuration

Config file: `~/.astro/agents/warehouse.yml`

**Supported databases:**

| Type | Driver | Description |
|------|--------|-------------|
| `snowflake` | Built-in | Snowflake Data Cloud |
| `postgres` | Built-in | PostgreSQL |
| `bigquery` | Built-in | Google BigQuery |
| `sqlalchemy` | Auto-detected | 25+ databases (DuckDB, Redshift, Trino, ClickHouse, Databricks, etc.) |

Credentials stored in `~/.astro/agents/.env` with `${VAR}` env interpolation.

### Schema Initialization (`warehouse-init`)

**Workflow:**
1. Read warehouse config → get database list
2. Search codebase for dbt models, gusty SQL frontmatter, AGENTS.md docs
3. Parallel warehouse discovery (one subagent per database via Task tool)
4. Discover categorical value families
5. Merge codebase context + warehouse metadata
6. Generate `.astro/warehouse.md` with:
   - Quick Reference table (concept → table mappings)
   - Categorical Column value families
   - Data Layer Hierarchy
   - Per-schema table details with row counts, descriptions, warnings
7. Pre-populate concept cache
8. Optionally append Quick Reference to `CLAUDE.md`

**Refresh:** `--refresh` flag preserves HTML comments, user-added Quick Reference entries, and descriptions while updating row counts.

## Integration Patterns with OpenCode

### As AGENTS.md Instructions

```json
{
  "instructions": [
    {
      "source": "astronomer-agents",
      "path": "https://github.com/astronomer/agents/blob/main/skills/airflow/SKILL.md",
      "description": "Airflow operations — DAG management, runs, troubleshooting"
    },
    {
      "source": "astronomer-agents",
      "path": "https://github.com/astronomer/agents/blob/main/skills/authoring-dags/SKILL.md",
      "description": "DAG authoring with 6-phase workflow"
    },
    {
      "source": "astronomer-agents",
      "path": "https://github.com/astronomer/agents/blob/main/skills/analyzing-data/SKILL.md",
      "description": "Warehouse querying with Jupyter kernel"
    }
  ]
}
```

### Via MCP (directly in OpenCode)

```json
{
  "mcpServers": {
    "airflow": {
      "command": "uvx",
      "args": ["astro-airflow-mcp", "--transport", "stdio"]
    }
  }
}
```

### Skill Cache Pattern

The `analyzing-data` skill demonstrates a powerful pattern for agentic coding tools:
- **Jupyter kernel** as persistent compute backend (avoids cold-start for each query)
- **Concept cache** (learn/lookup) — agent builds its own memory of data schemas
- **Pattern cache** (learn/lookup/record) — agent remembers successful query strategies
- **Table schema cache** — avoids repeated `INFORMATION_SCHEMA` queries
- All caches have TTL (7 days default) with explicit refresh commands

## Compatibility Matrix

| Tool | MCP Server | Skills | AGENTS.md/CLAUDE.md |
|------|:----------:|:------:|:-------------------:|
| **OpenCode** | Yes (manual MCP config) | Manual `instructions` URL | Full reader |
| **Claude Code** | Yes (plugin auto) | Plugin auto | Yes |
| **Cursor** | Yes (`mcp.json`) | `npx skills add -a cursor` | Yes |
| **Gemini CLI** | Yes (`gemini mcp add`) | — | Readers |
| **Codex CLI** | Yes (`codex mcp add`) | — | Readers |

## Key File References

- `AGENTS.md` — currently empty placeholder (plugin uses `.claude-plugin/` instead)
- `CLAUDE.md` — plugin development guide
- `.claude-plugin/plugin.json` — hooks: warm-uvx-cache (async SessionStart), kernel cleanup (Stop)
- `.claude-plugin/marketplace.json` — catalog with `strict: false`
- `.cursor-plugin/plugin.json` — Cursor-compatible hooks
- `astro-airflow-mcp/README.md` — full MCP server docs
- `prek.toml` — ruff, trailing-whitespace, doctoc hooks

## Full Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code / Cursor / OpenCode          │
├────────────────┬────────────────┬──────────────────────────┤
│  MCP Protocol  │  Plugin System  │  Skills (SKILL.md)       │
│  ↓             │  ↓              │  ↓                        │
│  astro-airflow │  .claude-plugin │  skills/<name>/           │
│  -mcp          │  /plugin.json   │  ├── SKILL.md             │
│  (uvx)         │                 │  ├── hooks/               │
│                │                 │  └── scripts/             │
├────────────────┴────────────────┴──────────────────────────┤
│                    Airflow Instance                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────────────────┐   │
│  │ REST API  │  │ Providers │  │ Postgres / Snowflake  │   │
│  │/api/v{1,2}│  │ Registry  │  │ / BigQuery / dbt      │   │
│  └───────────┘  └───────────┘  └───────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```
