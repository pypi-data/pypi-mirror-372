import logging

from click.testing import CliRunner

from fourdigits_cli.cli import main


def test_debug_option():
    runner = CliRunner()
    runner.invoke(main, ["docker"])
    assert logging.getLogger("fourdigits_cli").level == logging.INFO

    runner.invoke(main, ["--debug", "docker"])
    assert logging.getLogger("fourdigits_cli").level == logging.DEBUG
