import logging
import os
import re
import subprocess
import tempfile
import time

import click
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from fourdigits_cli.utils.docker import Docker, DockerException

logger = logging.getLogger(__name__)


@click.group()
def group(**options):
    pass


@group.command(
    name="sync:env", help="Shortcut for django:home/userapp/env -> env-docker"
)
@click.option(
    "--watch",
    is_flag=True,
    show_default=True,
    default=False,
    help="Watch for *.py file changes and copy back to service",
)
def sync_env(watch):
    sync_files("django", "home/userapp/env", "env-docker")
    if watch:
        watch_files("django", "home/userapp/env", "env-docker", "py")


@group.command(help="Sync folder in docker container to local folder")
@click.argument("service")
@click.argument("service_path")
@click.argument("local_path")
@click.option(
    "--watch",
    is_flag=True,
    show_default=True,
    default=False,
    help="Watch for file changes and copy back to service",
)
@click.option(
    "--watch-extensions",
    default="py",
    show_default=True,
    help="Comma separated list of file extensions to watch",
)
def sync(service, service_path, local_path, watch, watch_extensions):
    sync_files(service, service_path, local_path)
    if watch:
        watch_files(service, service_path, local_path, watch_extensions)


def sync_files(service, service_path, local_path):
    """Sync files from service to local path."""
    docker = Docker(None, None)
    local_path = os.path.abspath(local_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_local_path = os.path.join(tmp_dir, "local")
        click.echo(
            f"Copying files from {service}:{service_path} service to {local_path}"
        )
        try:
            docker.compose("cp", f"{service}:{service_path}", tmp_local_path)
        except DockerException:
            raise click.UsageError(
                f"Could not copy files from {service} service, is service running?"
            )
        # We use rsync to prevent index triggers in pycharm
        subprocess.run(
            [
                "rsync",
                "--archive",
                "--delete",
                "--update",
                f"{tmp_local_path}/",
                f"{local_path}/",
            ]
        )

    fix_symlinks(local_path)


def watch_files(service, service_path, local_path, extensions="py"):
    """Watch for file changes and copy back to service."""
    docker = Docker(None, None)
    click.echo(f"Watching for file changes in: {local_path} for {extensions} files")

    def on_modified(event):
        local_file_path = event.src_path
        file_path = local_file_path.removeprefix(f"{local_path}/")
        service_file_path = os.path.join(service_path, file_path)
        click.echo(f"Sync file: {file_path} -> {service_file_path}")
        try:
            docker.compose("cp", local_file_path, f"{service}:{service_file_path}")
        except DockerException as e:
            click.echo(f" * Error: {e}")

    event_handler = PatternMatchingEventHandler(
        patterns=[f"*.{extension}" for extension in extensions.split(",")]
    )
    event_handler.on_modified = on_modified

    # Start watcher
    observer = Observer()
    observer.schedule(event_handler, local_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def fix_symlinks(local_path):
    """Fix known symlinks"""
    python_bin = os.path.join(local_path, "bin", "python3")
    if os.path.islink(python_bin) and not os.path.exists(python_bin):
        fix_python_symlink(local_path)


def fix_python_symlink(local_path):
    # Find Python version
    python_version = None
    for file in os.listdir(os.path.join(local_path, "bin")):
        match = re.match(r"^python(\d\.\d+)$", file)
        if match:
            python_version = match.group(1)
            break

    # Find python bin
    try:
        python_bin = (
            subprocess.check_output(["which", f"python{python_version}"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        click.echo(
            click.style(
                f" - Warning: Could not fix symlink for python, is python{python_version} installed?",  # noqa: E501
                fg="yellow",
            )
        )
        return

    # Fix for .pyenv bin path
    if ".pyenv" in python_bin:
        partition = python_bin.partition(".pyenv")
        pyenv_versions = os.path.join(partition[0], partition[1], "versions")
        for pyenv_version_dir in os.listdir(pyenv_versions):
            if pyenv_version_dir.startswith(python_version):
                python_bin = os.path.join(
                    pyenv_versions, pyenv_version_dir, "bin", f"python{python_version}"
                )

    # Fix symlink
    local_bin_path = os.path.join(local_path, "bin", "python3")
    os.remove(local_bin_path)
    os.symlink(python_bin, local_bin_path)

    click.echo(f" - fix symlink bin/python3: {python_bin}")
