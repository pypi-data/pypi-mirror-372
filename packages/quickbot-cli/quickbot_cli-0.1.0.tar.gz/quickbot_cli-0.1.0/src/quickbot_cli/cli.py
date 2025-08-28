# SPDX-FileCopyrightText: 2025 Alexander Kalinovsky <a@k8y.ru>
#
# SPDX-License-Identifier: Apache-2.0

"""QuickBot CLI tool for generating project structures."""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import typer
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

app = typer.Typer(help="QuickBot CLI")

TEMPLATES_DIR = Path(__file__).parent / "templates"
# Module-level constants
DEFAULT_TEMPLATE = "basic"
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip"}


def load_template_spec(template_dir: Path) -> dict[str, Any]:
    """Load template specification from a template directory.

    Args:
        template_dir: Path to the template directory

    Returns:
        Dictionary containing template variables and post-tasks

    """
    spec_file = template_dir / "__template__.yaml"
    if not spec_file.exists():
        return {"variables": {}, "post_tasks": []}

    try:
        with spec_file.open(encoding="utf-8") as f:
            spec = yaml.safe_load(f) or {}
        return {
            "variables": spec.get("variables", {}),
            "post_tasks": spec.get("post_tasks", []) or [],
        }
    except yaml.YAMLError as e:
        typer.secho(f"Error parsing template spec: {e}", fg=typer.colors.RED)
        raise typer.Exit(1) from e


def _to_bool_like(*, value: str | bool | int) -> bool | None:
    """Convert a value to a boolean-like value.

    Args:
        value: Value to convert

    Returns:
        Boolean value or None if conversion is not possible

    """
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "t", "yes", "y", "1"}:
        return True
    if s in {"false", "f", "no", "n", "0"}:
        return False
    return None


def _handle_boolean_choices(prompt: str, choices: list[bool], *, default: bool | None) -> bool:
    """Handle boolean choice variables.

    Args:
        prompt: User prompt text
        choices: List of boolean choices
        default: Default value

    Returns:
        Selected boolean value

    Raises:
        typer.Exit: If invalid input is provided

    """
    raw = typer.prompt(f"{prompt} [y/n]", default=default)

    coerced = _to_bool_like(value=raw)
    if coerced is None:
        typer.secho(
            f"Value must be one of {choices} (accepted: true/false, yes/no, y/n, 1/0)",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    return coerced


def _handle_regular_choices(prompt: str, choices: list[str], default: str | None) -> str:
    """Handle regular choice variables.

    Args:
        prompt: User prompt text
        choices: List of available choices
        default: Default value

    Returns:
        Selected value

    Raises:
        typer.Exit: If invalid input is provided

    """
    val: str = typer.prompt(f"{prompt} {choices}", default=default)
    if val not in choices:
        typer.secho(f"Value must be one of {choices}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    return val


def ask_variables(spec: dict[str, Any], non_interactive: dict[str, Any]) -> dict[str, Any]:
    """Prompt user for template variables or use non-interactive values.

    Args:
        spec: Template specification containing variables
        non_interactive: Dictionary of non-interactive variable values

    Returns:
        Dictionary of resolved variable values

    """
    vars_spec = spec.get("variables", {})
    ctx: dict[str, Any] = {}

    for name, meta in vars_spec.items():
        if name in non_interactive and non_interactive[name] is not None:
            # Preserve the original type (especially for booleans)
            val = non_interactive[name]
        else:
            prompt = meta.get("prompt", name)
            default = meta.get("default")
            choices = meta.get("choices")

            if choices:
                if all(isinstance(c, bool) for c in choices):
                    val = _handle_boolean_choices(prompt=prompt, choices=choices, default=default)
                else:
                    val = _handle_regular_choices(prompt=prompt, choices=choices, default=default)
            else:
                val = typer.prompt(prompt, default=default)

        validate = meta.get("validate")
        if validate and not re.match(validate, str(val)):
            typer.secho(f"Invalid value for {name}: {val}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        ctx[name] = val

    ctx["package_name"] = "app"
    return ctx


def render_tree(
    env: Environment,
    template_root: Path,
    output_dir: Path,
    context: dict[str, Any],
    *,
    overwrite: bool,
    original_root: Path | None = None,
) -> None:
    """Render template tree to output directory.

    Args:
        env: Jinja2 environment for template rendering
        template_root: Root directory containing templates
        output_dir: Directory to output rendered files
        context: Context variables for template rendering
        overwrite: Whether to overwrite existing files
        original_root: Original template root for path calculation

    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use original_root for path calculation, fallback to template_root for backward compatibility
    root_for_path = original_root if original_root is not None else template_root

    for item in template_root.iterdir():
        if item.is_file():
            # Skip __template__.yaml
            if item.name == "__template__.yaml":
                continue
            if item.suffix == ".j2":
                # Render template file
                output_file = output_dir / item.stem
                if output_file.exists() and not overwrite:
                    # Skip existing file when overwrite is disabled
                    typer.secho(f"Warning: Skipping existing file: {output_file}", fg=typer.colors.YELLOW)
                    continue

                try:
                    template = env.get_template(str(item.relative_to(root_for_path)))
                    content = template.render(**context)
                    output_file.write_text(content, encoding="utf-8")
                except Exception as e:
                    typer.secho(f"Error rendering {item}: {e}", fg=typer.colors.RED)
                    raise
            else:
                # Copy non-template file
                output_file = output_dir / item.name
                if output_file.exists() and not overwrite:
                    # Skip existing file when overwrite is disabled
                    typer.secho(f"Warning: Skipping existing file: {output_file}", fg=typer.colors.YELLOW)
                    continue
                shutil.copy2(item, output_dir / item.name)
        elif item.is_dir():
            # Recursively render subdirectory
            sub_output = output_dir / item.name
            render_tree(env, item, sub_output, context, overwrite=overwrite, original_root=root_for_path)


def run_post_tasks(spec: dict[str, Any], context: dict[str, Any], cwd: Path) -> None:
    """Run post-generation tasks based on template specification.

    Args:
        spec: Template specification containing post-tasks
        context: Context variables for task execution
        cwd: Working directory for task execution

    """
    tasks = spec.get("post_tasks", []) or []
    for task in tasks:
        cond = task.get("when")
        if cond:
            env = Environment(undefined=StrictUndefined, autoescape=True)
            rendered_cond = env.from_string(str(cond)).render(**context)
            if rendered_cond.strip().lower() not in ("true", "yes", "1"):
                continue
        cmd = task.get("run")
        if not cmd:
            continue
        try:
            # This subprocess call is safe as it only executes commands from the template spec
            # which are controlled by the user/developer, not external input
            subprocess.run(cmd, cwd=cwd, check=True)  # noqa: S603
        except subprocess.CalledProcessError as e:
            typer.secho(f"Post-task failed: {cmd} -> {e}", fg=typer.colors.RED)


def _init_project(
    output: Path,
    template: str = DEFAULT_TEMPLATE,
    *,
    project_name: str | None = None,
    description: str | None = None,
    author: str | None = None,
    license_name: str | None = None,
    include_alembic: bool | None = None,
    include_i18n: bool | None = None,
    overwrite: bool = False,
    interactive: bool = False,
) -> None:
    """Generate a project with the structure app/ and optional Alembic / Babel."""
    template_dir = TEMPLATES_DIR / template
    if not template_dir.exists():
        msg = f"Template '{template}' not found"
        raise FileNotFoundError(msg)

    # Load template spec
    spec = load_template_spec(template_dir)

    # Prepare non-interactive values
    non_interactive = {
        "project_name": project_name,
        "description": description,
        "author": author,
        "license": license_name,
        "include_alembic": include_alembic,
        "include_i18n": include_i18n,
    }

    # Resolve variables
    if interactive:
        context = ask_variables(spec, non_interactive)
    else:
        # Use provided values or spec defaults without prompting
        context = {}
        for name, meta in (spec.get("variables", {}) or {}).items():
            if name in non_interactive and non_interactive[name] is not None:
                context[name] = non_interactive[name]
            else:
                context[name] = meta.get("default")
        context["package_name"] = "app"

    # Ensure project_name is set (fallback to output directory name)
    if not context.get("project_name"):
        context["project_name"] = output.name

    # Create output directory
    output.mkdir(parents=True, exist_ok=True)

    # Render templates
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=True,
    )

    render_tree(env, template_dir, output, context, overwrite=overwrite, original_root=template_dir)

    # Run post-tasks
    run_post_tasks(spec, context, output)

    # Optional modules are handled exclusively via post_tasks in template

    typer.secho(f"Project generated successfully in {output}", fg=typer.colors.GREEN)


@app.command()
def init(
    output: Path = typer.Option(".", help="Output directory (defaults to current directory)", show_default=False),
    template: str = typer.Option(DEFAULT_TEMPLATE, "--template", "-t", hidden=True),
    project_name: str | None = typer.Option(None, help="Project name", show_default=False),
    description: str | None = typer.Option(None, help="Description", show_default=False),
    author: str | None = typer.Option(None, help="Author", show_default=False),
    license_name: str | None = typer.Option(None, help="License", show_default=False),
    *,
    include_alembic: bool | None = typer.Option(
        None, help="Include Alembic (will prompt if not specified)", show_default=False
    ),
    include_i18n: bool | None = typer.Option(
        None, help="Include i18n (will prompt if not specified)", show_default=False
    ),
    overwrite: bool = typer.Option(default=False, help="Overwrite existing files"),
    interactive: bool = typer.Option(
        default=True,
        help="Interactive mode (if interactive is disabled, defaults will be taken from __template__.yaml)",
    ),
) -> None:
    """Initialize a new project in the specified directory."""
    _init_project(
        output=output,
        template=template,
        project_name=project_name,
        description=description,
        author=author,
        license_name=license_name,
        include_alembic=include_alembic,
        include_i18n=include_i18n,
        overwrite=overwrite,
        interactive=interactive,
    )


@app.command()
def version() -> None:
    """Show the version of quickbot-cli."""
    from quickbot_cli import __version__  # noqa: PLC0415

    typer.echo(f"quickbot-cli version {__version__}")


def main() -> None:
    """Run the main CLI application."""
    app()  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    main()
