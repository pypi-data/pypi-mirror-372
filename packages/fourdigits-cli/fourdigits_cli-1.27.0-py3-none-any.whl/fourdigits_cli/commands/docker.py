import json
import logging
import os
import string
from uuid import uuid4

import click
from packaging.version import InvalidVersion
from packaging.version import parse as version_parser

from fourdigits_cli.settings import DEFAULT_BUILD_ENVIRONMENT, get_environment_config
from fourdigits_cli.utils.docker import Docker, DockerException
from fourdigits_cli.utils.git import Git

logger = logging.getLogger(__name__)


@click.group(help="Docker helper command for auto building and pushing")
def group():
    pass


@group.command(help="Build Docker image for environment defined in pyproject.toml")
@click.argument("environment", default=DEFAULT_BUILD_ENVIRONMENT)
@click.option(
    "--version",
    help="Version to build. If no version is supplied, it will try to get the current git tag",  # noqa: E501
)
@click.option(
    "--repo",
    show_default=True,
    help="Repo to use in the image name. If no repo is supplied, it will use the value from the default config",  # noqa: E501
)
@click.option("--push", is_flag=True, show_default=True, default=False)
@click.option("--target")
@click.option("--file", default="Dockerfile", show_default=True)
@click.option("--context", default=".", show_default=True)
@click.option("--platform", default="linux/amd64", show_default=True)
@click.option("--build-arg", multiple=True)
@click.option(
    "--registry-domain",
    help="Defaults to docker-registry.fourdigits.nl, env override DOCKER_REGISTRY_DOMAIN",  # noqa: E501
)
@click.option("--registry-user", help="env override DOCKER_REGISTRY_USER")
@click.option("--registry-password", help="env override DOCKER_REGISTRY_PASSWORD")
@click.option("--default-branch", help="env override CI_DEFAULT_BRANCH")
@click.option("--no-rebuild", is_flag=True, default=False, show_default=True)
def build(environment, **options):
    config = get_environment_config(environment)
    docker = Docker(
        registry_user=options["registry_user"]
        or os.environ.get("DOCKER_REGISTRY_USER"),
        registry_password=options["registry_password"]
        or os.environ.get("DOCKER_REGISTRY_PASSWORD"),
        registry=options["registry_domain"]
        or os.environ.get("DOCKER_REGISTRY_DOMAIN", "docker-registry.fourdigits.nl"),
        image_user=config.docker_image_user,
    )

    version = validate_and_get_version(environment, version=options.get("version"))
    docker_repo = options.get("repo") or config.docker_repo
    default_branch = options.get("default_branch") or os.environ.get(
        "CI_DEFAULT_BRANCH", "main"
    )

    if not do_build(
        docker=docker,
        image=docker.get_image_name(docker_repo, version),
        no_rebuild=options.get("no_rebuild", False),
    ):
        click.echo("Skipping build, because image already exists on registry")
        return

    # Download the latest image to increase build process
    latest_image = docker.get_image_name(repo=docker_repo, tag=environment)
    try:
        docker.pull(latest_image)
    except DockerException:
        latest_image = None

    # Docker build, tag and push image
    build_image_name = uuid4().hex
    try:
        docker.build(
            build_image_name,
            file=options.get("file"),
            context=options.get("context"),
            target=options.get("target"),
            release_version=str(version),
            commit_hash=get_deployment_commit_hash(default_branch),
            cache_from=latest_image,
            build_args=options.get("build_arg"),
            platform=options.get("platform"),
        )
        for tag in [environment, str(version)]:
            docker.image_tag(
                build_image_name,
                docker.get_image_name(
                    repo=docker_repo,
                    tag=tag,
                ),
            )
            if options.get("push"):
                docker.push(
                    docker.get_image_name(
                        repo=docker_repo,
                        tag=tag,
                    )
                )
    except DockerException as e:
        raise click.UsageError(e)


@group.command(help="Create new tag for existing tag on registry")
@click.argument("src_tag")
@click.argument("new_tag")
@click.option(
    "--build-env-config",
    default=DEFAULT_BUILD_ENVIRONMENT,
    help="Environment config to use, default is build environment",
)
@click.option(
    "--repo",
    show_default=True,
    help="Repo to use in the image name. If no repo is supplied, it will use the value from the default config",  # noqa: E501
)
@click.option(
    "--registry-domain",
    help="Defaults to docker-registry.fourdigits.nl, env override DOCKER_REGISTRY_DOMAIN",  # noqa: E501
)
@click.option("--registry-user", help="env override DOCKER_REGISTRY_USER")
@click.option("--registry-password", help="env override DOCKER_REGISTRY_PASSWORD")
def tag(src_tag, new_tag, **options):
    config = get_environment_config(options.get("build_env_config"))
    docker = Docker(
        registry_user=options["registry_user"]
        or os.environ.get("DOCKER_REGISTRY_USER"),
        registry_password=options["registry_password"]
        or os.environ.get("DOCKER_REGISTRY_PASSWORD"),
        registry=options["registry_domain"]
        or os.environ.get("DOCKER_REGISTRY_DOMAIN", "docker-registry.fourdigits.nl"),
        image_user=config.docker_image_user,
    )

    docker_repo = options.get("repo") or config.docker_repo

    src_image = docker.get_image_name(docker_repo, src_tag)
    new_image = docker.get_image_name(docker_repo, new_tag)

    try:
        manifest = json.loads(docker.manifest("inspect", src_image))
    except DockerException as e:
        raise click.UsageError(f"Could not get src manifest: {e}")

    # Based on manifest get the correct src_image
    if manifest["mediaType"] == "application/vnd.docker.distribution.manifest.v2+json":
        # Valid manifest type for manifest create with standard image path
        pass
    elif (
        manifest["mediaType"]
        == "application/vnd.docker.distribution.manifest.list.v2+json"
    ):
        # Because its a list type we get the first manifest,
        # and use direct digest reference for the create
        src_image = (
            docker.get_image_name(docker_repo)
            + "@"
            + manifest["manifests"][0]["digest"]
        )
    else:
        raise click.UsageError(f"Got unkown manifest type: {manifest['mediaType']}")

    # Create new tag
    try:
        docker.manifest("create", new_image, src_image)
    except DockerException as e:
        raise click.UsageError(f"Could not create tag: {e}")

    # Push new tag
    try:
        docker.manifest("push", new_image)
    except DockerException as e:
        raise click.UsageError(f"Could not push image: {e}")

    click.echo(f"New tag created {new_image} from {src_image}")


def do_build(docker: Docker, image: str, no_rebuild: bool):
    if not no_rebuild:
        return True

    try:
        docker.manifest("inspect", image)
        return False
    except DockerException:
        return True


def validate_and_get_version(environment, version=None):
    if version:
        if validate_version(environment, version):
            return version
        elif validate_git_commithash(environment, version):
            return version
        else:
            raise click.UsageError(
                f"Invalid version format ({version}) for {environment}"
            )

    if environment not in ["acc", "prd"]:
        return Git().rev_parse("--short=8", "HEAD").strip()

    current_commit_tags = Git().tag("--points-at", "HEAD").splitlines()
    for tag_version in current_commit_tags:
        if validate_version(environment, version):
            return tag_version

    if environment == "acc":
        raise click.UsageError(
            f"Could not get valid version tag for ACC on current commit ({current_commit_tags}), valid format is: <major>.<minor>.<patch>rc<number>"  # noqa: E501
        )
    elif environment == "prd":
        raise click.UsageError(
            f"Could not get valid version tag for PRD on current commit ({current_commit_tags}), valid format is: <major>.<minor>.<patch>"  # noqa: E501
        )


def validate_version(environment, version):
    try:
        version = version_parser(version.strip())
    except (IndexError, InvalidVersion):
        return False

    if environment == DEFAULT_BUILD_ENVIRONMENT:
        return False
    if environment == "acc" and version.pre:
        return True
    elif environment == "prd" and not (
        version.pre or version.post or version.dev or version.local
    ):
        return True
    elif environment in ["acc", "prd"]:
        return False
    return True


def validate_git_commithash(environment, version):
    """
    A commit hash is valid for 'tst' only, and should match a specific format

    Git uses commit hashes in SHA-1 format: 40 chars. The shortened version has no
    defined length other than 'what is needed to make it unique within the repository.'
    git-cli uses 7 chars for `--abbrev-commit`. Github uses 7 chars in it's UI,
    while Gitlab has 8 chars.
    """
    if environment not in ["tst", DEFAULT_BUILD_ENVIRONMENT]:
        return False

    version = version.strip()
    return version.strip(string.hexdigits) == "" and 7 <= len(version) <= 40


def get_deployment_commit_hash(default_branch):
    """
    Retrieves the commit hash from the default branch to use for deployment tracking.

    Deployment tracking requires the commit hash associated with the main branch
    (or the primary branch used for deployment). This function determines the
    merge base between the current HEAD and the default branch. If this fails,
    it falls back to returning the current HEAD's commit hash.
    """
    git = Git()
    try:
        # Ensure the default branch is up to date from the remote.
        git.fetch("origin", default_branch)

        # Find the merge base, which represents the common ancestor commit
        # between the current branch (or tag) and the default branch. This is
        # used to track the commit relevant to the main tree for deployments.
        return git.merge_base(f"origin/{default_branch}", "HEAD")
    except Exception:
        # If fetching or determining the merge base fails, return the current
        # HEAD commit hash.
        return git.rev_parse("HEAD").strip()
