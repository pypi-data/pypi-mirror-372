import os

from setuptools import Command, find_packages, setup

from fourdigits_cli import __version__


def readme():
    with open("README.md") as f:
        return f.read()


class CreateTagCommand(Command):
    description = "Create release tag"
    user_options = []

    def run(self):
        os.system(f"git tag -a {__version__} -m 'v{__version__}'")
        os.system("git push --tags")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


setup(
    name="fourdigits-cli",
    version=__version__,
    description="FourDigits CLI tool",
    long_description=readme(),
    long_description_content_type="text/markdown",
    cmdclass={"tag": CreateTagCommand},
    packages=find_packages(include=["fourdigits_cli", "fourdigits_cli.*"]),
    entry_points={
        "console_scripts": [
            "4d = fourdigits_cli.cli:main",
            "fourdigits = fourdigits_cli.cli:main",
        ]
    },
    python_requires=">= 3.9",
    install_requires=[
        "click~=8.1.3",
        "tomli~=2.0.1",
        "fabric~=3.2.2",
        "packaging",
        "requests",
        "watchdog",
        "exonetapi",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
            "pytest",
            "pytest-check",
            "pytest-cov",
        ]
    },
)
