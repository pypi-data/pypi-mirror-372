# Minitap Miniflow CLI

A CLI to run miniflows locally.

## Installation

To install the Minitap Miniflow CLI, you can use pip:

```bash
pip install minitap-miniflow
```

## Usage

The Miniflow CLI provides several commands to interact with your Miniflow account and execute flows.

### Authentication

**Login**
To authenticate with your Miniflow account, run the `login` command. This will open a browser window for you to log in.

```bash
miniflow login
```

**Logout**
To log out from your Miniflow account, use the `logout` command.

```bash
miniflow logout
```

**Check Status**
To check the currently authenticated user, use the `whoami` command.

```bash
miniflow whoami
```

### Executing Flows

**Run a Flow**
You can execute a flow by its ID using the `run` command.

```bash
miniflow run <FLOW_ID>
```

Replace `<FLOW_ID>` with the actual ID of the flow you want to run.

## Development
```bash
uv venv 
source .venv/bin/activate
uv sync
```
This project uses `ruff` for linting and formatting.

To install the development dependencies, run:
```bash
ruff format 
ruff check --fix
```
