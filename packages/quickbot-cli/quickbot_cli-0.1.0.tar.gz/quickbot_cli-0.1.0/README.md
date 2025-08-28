<!--
SPDX-FileCopyrightText: 2025 Alexander Kalinovsky <a@k8y.ru>

SPDX-License-Identifier: Apache-2.0
-->

# quickbot_cli
QuickBot CLI for scaffolding new projects from templates.

### Features
- Generate a ready-to-run QuickBot app structure from templates
- Optional modules (e.g., Alembic migrations, i18n) included/excluded via flags

## Installation
You can install the CLI into your environment:

```bash
uv pip install quickbot-cli
```

Alternatively, for local development in this repo:

```bash
uv pip install -e .[dev]
```

## Usage
Show help:

```bash
uv run quickbot --help
uv run quickbot init --help
```

Generate a project into a target directory (default template: "basic"):

```bash
uv run quickbot init ./my_bot \
  --template basic \
  --project-name my_bot \
  --description "My awesome bot" \
  --author "Jane Doe" \
  --license-name MIT \
  --include-alembic \
  --include-i18n \
  --overwrite
```

Key options:
- `--template, -t`: template name (default: `basic`)
- `--project-name`: project name used during rendering
- `--description`: short description
- `--author`: author name
- `--license-name`: license identifier (e.g., MIT)
- `--include-alembic/--no-include-alembic`: include Alembic files (default: on)
- `--include-i18n/--no-include-i18n`: include i18n files (default: on)
- `--overwrite`: overwrite existing files when rendering

## Templates
Built-in templates live under `src/quickbot_cli/templates/`. The default is `basic` and includes a minimal app layout plus optional Alembic/i18n modules.

Each template can include a `__template__.yaml` file describing variables and post-generation tasks. Example:

```yaml
variables:
  project_name:
    prompt: Project name
    default: my_project
  include_alembic:
    prompt: Include Alembic?
    choices: ["yes", "no"]
    default: "yes"
post_tasks:
  - when: "{{ include_alembic }}"
    run: ["echo", "alembic_initialized"]
```

Template files use the `.j2` suffix and are rendered to the output path with variables made available to Jinja2. Non-`.j2` files are copied as-is.

## Development
Clone the repo and install dev deps:

```bash
uv pip install -e .[dev]
```

Run tests:

```bash
uv run python run_tests.py
# or
uv run -m pytest tests/ -v --tb=short
```

Code style and tooling:
- Ruff and MyPy configs are in `pyproject.toml`
- Pre-commit hooks: `.pre-commit-config.yaml`

## License
MIT. See `LICENSES/MIT.txt`.
