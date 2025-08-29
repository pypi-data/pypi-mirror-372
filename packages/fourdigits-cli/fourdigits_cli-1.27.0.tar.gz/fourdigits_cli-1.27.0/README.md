# FourDigits CLI

A command line tool to make development and deployment easier within Four Digits.

It has the following commands:

1. "docker"
    - "build": Build docker images in our Gitlab CI pipelines
    - "tag": Create new Docker tag for existing Docker tag on registry
2. "gitlab"
    - "fix-coverage-paths": Change the generated coverage.xml so Gitlab can show coverage visualization in merge requests
3. "exonet"
   - "deploy": Deploy a project to Exonet
   - "db:download": Download a database from Exonet and import it locally
   - "db:copy": Copy a database from one environment to another
4. "docker-compose"
   - "sync": Sync files from a service to local folder
   - "sync:env": Shortcut for django:home/userapp/env -> env-docker

## Install

With [pipx](https://github.com/pypa/pipx):

    pipx install fourdigits-cli

With [pip](https://github.com/pypa/pip):

    sudo pip install --break-system-packages fourdigits-cli

With [uv tool](https://docs.astral.sh/uv/concepts/tools/#tools):

    uv tool install fourdigits-cli

## Upgrade

With pipx:

    pipx upgrade fourdigits-cli

With pip:

    sudo pip install --upgrade fourdigits-cli

With uv tool:

    uv tool upgrade fourdigits-cli --upgrade

### Enable auto complete

#### bash

Add this to `~/.bashrc`:

```shell
eval "$(_4D_COMPLETE=bash_source 4d)"
eval "$(_FOURDIGITS_COMPLETE=bash_source fourdigits)"
```

#### Zsh

Add this to `~/.zshrc`:

```shell
eval "$(_4D_COMPLETE=zsh_source 4d)"
eval "$(_FOURDIGITS_COMPLETE=zsh_source fourdigits)"
```

## Usage

After installation the cli tool is available under `fourdigits` and `4d`.
For more information use:

    fourdigits --help

### Example: Build a docker image and deploy it to the test environment

Build an image for the `tst` environment and upload it to our registry:

```
$ fourdigits docker build tst --push
Docker build image <docker_tag>
 - file=Dockerfile
 - context=.
 - target=None
Docker create tag <tmp_tag> -> docker-registry.fourdigits.nl/fourdigits/<project>:tst
Docker push tag docker-registry.fourdigits.nl/fourdigits/<project>:tst
Docker create tag <tmp_tag> -> docker-registry.fourdigits.nl/fourdigits/<project>:<docker_tag>
Docker push tag docker-registry.fourdigits.nl/fourdigits/wijsproductportals:<docker_tag>
```

To deploy this to the `tst` environment, use the `docker_tag` (not the `tmp_tag`) from the previous step:

```bash
$ fourdigits exonet deploy tst <docker_tag>
{"id":...,"number":<number>,...}
```

You can see the progress of the deployment pipeline on https://drone.exonet.nl/exonet/containers-fourdigits/<number>. 

## Troubleshooting

### unauthorized

If you get:
```
unauthorized: unauthorized to access repository: fourdigits/<project>, action: push: unauthorized to access repository: fourdigits/<project>, action: push
```

You need to login to the registry:

```bash
docker login
docker login docker-registry.fourdigits.nl
```

## Project configuration

The project is configured in the `pyproject.toml` file, available options and their defaults:

```toml
[project]
name = "default-project"

[tool.fourdigits]
exonet_project_name="<default is project name>"
docker_repo="<default is project name>"
slack_channel="<default is project name>"
docker_image_user="fourdigits"
# If a different server with same exonet setup is used, like industrial-auctions. Otherwise, don't define for default
database_ssh_username="admin@db01.industrial-auctions.com"
application_ssh_host="app01.industrial-auctions.com"
database_host="db01.industrial-auctions.com"

[tool.fourdigits.envs.<environment anem>]
exonet_environment="<default is environment name>"
# Every setting can be overridden per environment
slack_channel="custom-channel"
```

### Example project with separate nextjs

```toml
[project]
name = "django-project"

[tool.fourdigits]
# default to project name

[tool.fourdigits.envs.tst]

[tool.fourdigits.envs.acc]

[tool.fourdigits.envs.prd]

[tool.fourdigits.envs.nextjs_tst]
exonet_project_name = "nextjs"
exonet_environment = "tst"
docker_repo = "nextjs"

[tool.fourdigits.envs.nextjs_acc]
exonet_project_name = "nextjs"
exonet_environment = "acc"
docker_repo = "nextjs"

[tool.fourdigits.envs.nextjs_prd]
exonet_project_name = "nextjs"
exonet_environment = "prd"
docker_repo = "nextjs"
```

## Development

Running:

    make develop

creates a virtualenv `env/` with all development requirements.

To activate it:

   source env/bin/activate

## Releasing

To make a new release available on pypi, follow these steps:

1. Update version by edit `fourdigits_cli/__init__.py` and commit.
2. Run: `make push-version`
3. Update the installation of fourdigits-cli in https://gitlab.com/fourdigits/utils/docker-pipeline-image/-/blob/main/Dockerfile
to the newest version.
