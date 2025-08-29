from dataclasses import MISSING, fields

import click

from fourdigits_cli.settings import (
    DEFAULT_BUILD_ENVIRONMENT,
    GROUP_NAME_DEFAULTS,
    PROJECT_NAME_DEFAULTS,
    EnvironmentConfig,
)


@click.group(help="Additional help topics")
def group():
    pass


@group.command(name="config", help="Explain pyproject.toml configuration and options")
def config_help():
    # Helpers for styled output
    def header(text: str):
        click.secho(text, fg="cyan", bold=True)

    def bullet(label: str, desc: str = ""):
        if desc:
            click.echo("  • " + click.style(label, bold=True) + f": {desc}")
        else:
            click.echo(f"  • {label}")

    def para(text: str, fg: str | None = None, dim: bool = False):
        click.secho(text, fg=fg, dim=dim)

    def code_block(lines: list[str]):
        for line in lines:
            click.secho(f"    {line}", fg="green")

    para(
        "FourDigits CLI configuration lives in pyproject.toml under [tool.fourdigits].",
    )
    click.echo()

    header("Structure")
    bullet("[project]", "Standard project metadata; we use `name` as a default.")
    bullet("[tool.fourdigits]", "Global defaults for all environments.")
    bullet("[tool.fourdigits.envs.<environment>]", "Per-environment overrides.")
    click.echo()

    # Collect dynamic defaults
    def default_hint(field_name: str, default_value):
        if field_name == "name":
            return "Defaults to [project.name]"
        if field_name in PROJECT_NAME_DEFAULTS:
            return "Defaults to [project.name]"
        if field_name in GROUP_NAME_DEFAULTS:
            return "Defaults to the environment key"
        if default_value is MISSING or default_value == "":
            return "Default: <empty>"
        return f"Default: {default_value!r}".replace("'", '"')

    header("Global Options (with defaults)")
    for f in fields(EnvironmentConfig):
        bullet(f.name, default_hint(f.name, f.default))
    click.echo()

    header("Environment Options (override per environment)")
    para(
        "All global options can be overridden under [tool.fourdigits.envs.<env>].",
        dim=True,
    )
    for f in fields(EnvironmentConfig):
        hint = default_hint(f.name, f.default)
        if f.name in GROUP_NAME_DEFAULTS:
            hint = "Defaults to the environment key"
        bullet(f.name, hint)
    click.echo()

    header("Notes")
    bullet(
        f"Implicit '{DEFAULT_BUILD_ENVIRONMENT}' env",
        "Used by `fourdigits docker build` when no environment is specified.",
    )
    bullet("Overrides", "Env values override global values.")
    click.echo()

    header("Minimal Example")
    code_block(
        [
            "[project]",
            'name = "my-project"',
            "",
            "[tool.fourdigits]",
            "# set global defaults here (optional)",
            "",
            "[tool.fourdigits.envs.tst]",
            (
                '# exonet_environment defaults to "tst"'
                if "exonet_environment" in GROUP_NAME_DEFAULTS
                else ""
            ),
            "",
            "[tool.fourdigits.envs.acc]",
            "",
            "[tool.fourdigits.envs.prd]",
        ]
    )
