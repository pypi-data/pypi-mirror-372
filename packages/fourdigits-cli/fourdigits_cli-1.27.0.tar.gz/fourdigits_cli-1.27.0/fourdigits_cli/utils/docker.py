import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class DockerException(Exception):
    pass


class Docker:
    """
    Wrapper around the docker cli command
    """

    def __init__(
        self,
        registry_user="",
        registry_password="",
        registry="docker.io",
        image_user="fourdigits",
    ):
        self.registry_user = registry_user
        self.registry_password = registry_password
        self.registry = registry
        self.image_user = image_user
        self._logged_in = False

    def login(self):
        if self._logged_in or not self.registry_user or not self.registry_password:
            return

        logger.debug(f"Docker login to {self.registry} with user {self.registry_user}")
        result = subprocess.run(
            [
                "docker",
                "login",
                self.registry,
                f"--username={self.registry_user}",
                f"--password={self.registry_password}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ConnectionError(
                f"Could not login to {self.registry} with user {self.registry_user}: {result.stderr}"  # noqa: E501
            )
        self._logged_in = True

    def run(self, command: list) -> str:
        self.login()

        if command[0] != "docker":
            command = ["docker"] + command

        logger.debug("Docker run: " + " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise DockerException(f"Executing {command}:\n\n{result.stderr}")

        logger.debug(result.stdout)
        return result.stdout

    def pull(self, tag):
        return self.run(["pull", tag])

    def build(
        self,
        tag,
        file="Dockerfile",
        context=".",
        target=None,
        release_version="",
        commit_hash="",
        cache_from=None,
        build_args=None,
        platform="linux/amd64",
    ):
        logger.info(f"Docker build image {tag}")
        logger.info(f" - file={file}")
        logger.info(f" - context={context}")
        logger.info(f" - target={target}")
        return self.run(
            list(
                filter(
                    None,
                    [
                        "build",
                        "--pull",
                        f"--target={target}" if target else None,
                        f"--tag={tag}",
                        f"--file={file}",
                        f"--platform={platform}",
                        f"--cache-from={cache_from}" if cache_from else None,
                        f"--build-arg=RELEASE_VERSION={release_version}",
                        f"--build-arg=COMMIT_HASH={commit_hash}",
                        (
                            "--secret=id=pip_extra_index_url,env=PIP_EXTRA_INDEX_URL"
                            if "PIP_EXTRA_INDEX_URL" in os.environ
                            else None
                        ),
                        *[f"--build-arg={arg}" for arg in build_args or []],
                        context,
                    ],
                )
            )
        )

    def image_tag(self, tag, new_tag):
        logger.info(f"Docker create tag {tag} -> {new_tag}")
        return self.run(["image", "tag", tag, new_tag])

    def push(self, tag):
        logger.info(f"Docker push tag {tag}")
        self.run(["image", "push", tag])

    def get_image_name(self, repo, tag=None):
        image_name = f"{self.registry}/{self.image_user}/{repo}"

        return f"{image_name}:{tag}" if tag else image_name

    def compose(self, *args):
        return self.run(["compose", *args])

    def manifest(self, *args):
        return self.run(["manifest", *args])
