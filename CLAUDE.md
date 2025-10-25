# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mail Muxer (mmuxer) is a Python-based IMAP email filtering tool that monitors mailboxes and applies rules to incoming emails. It provides an alternative to web-based email filters with a simple YAML configuration format.

## Development Commands

### Testing
```bash
# Run all tests (uses pytest-bg-process to start mock IMAP server)
pytest

# Run specific test file
pytest tests/test_condition.py

# Run specific test
pytest tests/test_condition.py::test_name
```

```bash
# Check code quality before commiting
pre-commit run --all-files
```

### Running commands

To run a command, use `pdm run [cmd]`. The will load the virtualenv


### Running the Application
```bash
# Check configuration
mmuxer check --config-file config.yaml

# Monitor inbox (main use case)
mmuxer monitor --config-file config.yaml

# Apply rules to existing emails
mmuxer tidy --config-file config.yaml --folder INBOX

# Manage folders
mmuxer folder --config-file config.yaml compare-destinations

# Export rules to Sieve format
mmuxer sieve-export --config-file config.yaml --dest-file rules.sieve
```

## Architecture

### Core Components

**State Management** (`config_state.py`):
- Central `State` singleton that holds configuration, rules, scripts, and mailbox connection
- Handles config loading/reloading from YAML files
- Manages IMAP connection lifecycle with SSL context configuration

**Models** (`mmuxer/models/`):
- **Rule** (`rule.py`): Combines conditions and actions. Rules are evaluated in order and processing stops unless `keep_evaluating=True`
- **Condition** (`condition.py`): Recursive structure supporting `From`, `To`, `Subject`, `Body` base conditions combined with `ALL`, `ANY`, `NOT` operators. Uses Pydantic with frozen models for immutability
- **Action** (`action.py`): `MoveAction`, `DeleteAction`, `FlagAction`, `UnflagAction`. Actions can be defined inline or referenced by name from config
- **Script** (`script.py`): Dynamically loads Python modules to execute custom logic on messages matching conditions
- **Settings** (`settings.py`): IMAP connection settings with environment variable support

**Workers** (`workers.py`):
- `MonitorWorker`: Main thread that uses IMAP IDLE to watch for new messages and apply rules
- `WatcherWorker`: Watches config file for changes and triggers hot-reload (experimental feature using watchfiles with polling for vim compatibility)

**CLI** (`mmuxer/cli/`):
- Built with Typer
- Commands organized in `__main__.py` with custom `OrderCommands` group to preserve command ordering
- Main commands: `monitor`, `tidy`, `sieve-export`
- Utility commands: `check`, `folder`

### Key Design Patterns

**Rule Application Flow**:
1. Message arrives (monitor) or is fetched (tidy)
2. Rules evaluated sequentially via `apply_list()` in `rule.py`
3. Each rule checks condition with `condition.eval(message)`
4. If matched, actions execute via `action.apply(mailbox, message, dry_run)`
5. Processing stops unless `keep_evaluating=True`
6. Scripts run after all rules

**Configuration Loading**:
- YAML parsed into Pydantic models with custom `parse_data()` methods
- Settings can use environment variables (case-insensitive)
- Actions support named references (`actions: ["delete"]`) resolved from `state.actions` dict
- Parse errors formatted with context using custom `ParseException`

**Sieve Export**:
- Rules and conditions implement `to_sieve()` methods
- Exported rules maintain same logic as IMAP implementation

### Testing Infrastructure

Tests use a mock IMAP server from `aioimaplib` (see `tests/imap_server.py`) started automatically by pytest-bg-process. The background server command and log file are configured in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Python Environment

- Requires Python 3.9-3.12 (constrained by pydantic-core compatibility)
- Uses PDM for dependency management and building
- Key dependencies: typer, pydantic, imap-tools, watchfiles, sievelib
- Line length: 99 characters (black/isort config)

## Important Notes

- The `associated_folder` attribute is dynamically added to `MailMessage` objects to track which folder a message came from (used by `MoveAction.skip()`)
- SSL cipher configuration is critical for some servers - see `make_ssl_context()` in `config_state.py`
- IMAP connection uses automatic reconnection on `IMAP4.abort` exceptions
- Config hot-reload uses polling instead of inotify due to vim's atomic write behavior
