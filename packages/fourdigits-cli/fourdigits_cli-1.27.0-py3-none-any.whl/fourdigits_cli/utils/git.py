import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class GitException(Exception):
    pass


class Git:
    """
    Wrapper around the git cli command
    """

    def __init__(self, remote_name="origin"):
        self.remote_name = remote_name
        self.is_gitlab_pipeline = False
        self.gitlab_url = None

        self._check_gitlab_pipeline()

    def _check_gitlab_pipeline(self):
        ci_job_token = os.environ.get("CI_JOB_TOKEN")
        ci_project_path = os.environ.get("CI_PROJECT_PATH")
        ci_server_host = os.environ.get("CI_SERVER_HOST")
        if ci_job_token:
            self.is_gitlab_pipeline = True
            self.gitlab_url = f"https://gitlab-ci-token:{ci_job_token}@{ci_server_host}/{ci_project_path}.git"  # noqa: E501

    @staticmethod
    def run(command: list[str]) -> str:
        if command[0] != "git":
            command = ["git"] + command

        logger.debug("Git run: " + " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise GitException(f"Executing {command}:\n\n{result.stderr}")

        return result.stdout

    def ls_remote(self, *arguments) -> str:
        return self.run(
            [
                "ls-remote",
                *arguments,
                self.gitlab_url if self.is_gitlab_pipeline else self.remote_name,
            ]
        )

    def describe(self, *arguments) -> str:
        return self.run(
            [
                "describe",
                *arguments,
            ]
        )

    def rev_parse(self, *arguments) -> str:
        return self.run(
            [
                "rev-parse",
                *arguments,
            ]
        )

    def tag(self, *arguments) -> str:
        return self.run(
            [
                "tag",
                *arguments,
            ]
        )

    def fetch(self, *arguments) -> str:
        return self.run(["fetch", *arguments])

    def merge_base(self, *arguments) -> str:
        return self.run(["merge-base", *arguments])
