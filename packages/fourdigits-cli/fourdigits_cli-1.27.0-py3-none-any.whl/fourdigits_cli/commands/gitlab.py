import os
from xml.etree import ElementTree

import click


@click.group()
def group():
    pass


@group.command()
@click.argument("path", required=False)
@click.option("--path-prefix", default="src", show_default=True)
@click.option("--fail-silent", is_flag=True, show_default=True, default=False)
def fix_coverage_paths(path=None, path_prefix="src", fail_silent=False):
    """
    Add prefix to all filenames in given coverage xml,
    to fix gitlab pull request coverage visualization.
    This is needed if you run your coverage from a subdirectory,
    like docker compose with a src folder.

    PATH: defaults to src/coverage.xml
    """
    if not path:
        path = os.path.join(os.getcwd(), "src/coverage.xml")

    if not os.path.isfile(path):
        raise_error_or_exit_silently(f"File not found: {path}", fail_silent)

    try:
        tree = ElementTree.parse(path)
        for class_element in tree.findall(".//class"):
            filename = class_element.get("filename")
            if filename and not str(filename).startswith(f"{path_prefix}/"):
                class_element.set("filename", os.path.join(path_prefix, filename))
        tree.write(path)
    except Exception as e:
        raise_error_or_exit_silently(str(e), fail_silent)


def raise_error_or_exit_silently(message, silent=False):
    if silent:
        click.echo(message)
        exit(0)
    else:
        raise click.UsageError(message)
