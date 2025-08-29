import logging
import os
from dataclasses import dataclass, field

import click
import tomli

logger = logging.getLogger(__name__)

PROJECT_NAME_DEFAULTS = [
    "exonet_project_name",
    "docker_repo",
    "slack_channel",
]

GROUP_NAME_DEFAULTS = [
    "exonet_environment",
]

DEFAULT_BUILD_ENVIRONMENT = "build"


@dataclass(frozen=True)
class EnvironmentConfig:
    """
    Configuration for an environment: test, acceptation, production, etc.
    For Exonet projects, this is tst, acc, prd.

    In pyproject.toml, this is defined as:

    ```toml
    [tool.fourdigits.envs.tst]

    [tool.fourdigits.envs.acc]

    [tool.fourdigits.envs.prd]

    [tool.fourdigits.envs.nextjs_tst]
    exonet_project_name = "nextjs"
    docker_repo = "nextjs"

    [tool.fourdigits.envs.nextjs_acc]
    exonet_project_name = "nextjs"
    docker_repo = "nextjs"

    [tool.fourdigits.envs.nextjs_prd]
    exonet_project_name = "nextjs"
    docker_repo = "nextjs"
    ```
    """

    name: str = ""
    exonet_project_name: str = ""
    exonet_environment: str = ""
    docker_repo: str = ""
    slack_channel: str = ""
    docker_image_user: str = "fourdigits"
    database_ssh_username: str = "admin@container-db01.fourdigits.nl"
    # Used as argument in pg_dump as admin on the database server.
    # Note that for the IA server this is the same as database_ssh_username
    # without user, but on the default server this is different.
    # If you want to know why: ask Exonet.
    database_host: str = "container-db01"
    application_ssh_host: str = "container-docker01.fourdigits.nl"


@dataclass(frozen=True)
class Config:
    """
    Configuration for the fourdigits CLI.

    All environment settings can be set in this configuration as defaults.
    """

    environments: dict[str, EnvironmentConfig] = field(default_factory=dict)


def load_config(py_project_paths: list):
    config = {}
    for path in py_project_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    config = tomli.load(f)
            except tomli.TOMLDecodeError as e:
                logger.warning(f"Could not load pyproject.toml file: {e}")
                config = {}

    global_config = config.get("tool", {}).get("fourdigits", {})
    global_config["name"] = global_config.get("name") or config.get("project", {}).get(
        "name", ""
    )

    # Set defaults
    for key in PROJECT_NAME_DEFAULTS:
        if not global_config.get(key):
            global_config[key] = global_config["name"]

    # Get environments
    environments = {}

    config_envs: dict[str, dict] = global_config.get("envs", {})
    config_envs.setdefault(DEFAULT_BUILD_ENVIRONMENT, {})
    for group, group_config in config_envs.items():
        kwargs = {
            key: value
            for key, value in group_config.items()
            if key in EnvironmentConfig.__annotations__
        }

        # Fill missing keys with global_config
        for key in EnvironmentConfig.__annotations__:
            if not kwargs.get(key) and global_config.get(key):
                kwargs[key] = global_config.get(key)

        # Set defaults
        for key in GROUP_NAME_DEFAULTS:
            if not kwargs.get(key):
                kwargs[key] = group

        environments[group] = EnvironmentConfig(**kwargs)
    return Config(environments=environments)


DEFAULT_CONFIG = load_config(
    [
        os.path.join(os.getcwd(), "pyproject.toml"),
        os.path.join(os.getcwd(), "src", "pyproject.toml"),
    ]
)


def get_environment_config(environment: str) -> EnvironmentConfig:
    if environment not in DEFAULT_CONFIG.environments:
        raise click.UsageError("Environment doesn't exists in the pyproject.toml")
    return DEFAULT_CONFIG.environments.get(environment)
