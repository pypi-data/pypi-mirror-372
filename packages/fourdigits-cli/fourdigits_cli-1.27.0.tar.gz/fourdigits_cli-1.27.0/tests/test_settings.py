from pytest_check import check

from fourdigits_cli.settings import DEFAULT_BUILD_ENVIRONMENT, load_config
from tests import DATA_DIR


def test_load_config_valid():
    config = load_config([DATA_DIR / "valid.toml"])

    # test environments
    for env, name in {
        "tst": {
            "name": "valid-name",
            "exonet_project_name": "tst-project",
            "exonet_environment": "tst-environment",
            "docker_repo": "tst-repo",
            "slack_channel": "tst-channel",
            "docker_image_user": "tst-image-user",
        },
        "acc": {
            "name": "valid-name",
            "exonet_project_name": "valid-name",
            "exonet_environment": "acc",
            "docker_repo": "only-custom-repo",
            "slack_channel": "valid-name",
            "docker_image_user": "valid-image-user",
        },
        "prd": {
            "name": "valid-name",
            "exonet_project_name": "valid-name",
            "exonet_environment": "prd",
            "docker_repo": "valid-repo",
            "slack_channel": "only-custom-channel",
            "docker_image_user": "valid-image-user",
        },
    }.items():
        for key, value in name.items():
            with check:
                assert (
                    getattr(config.environments[env], key) == value
                ), f"{env}.{key}"  # noqa: E501
        with check:
            assert not hasattr(config.environments[env], "extra_option")


def test_load_config_invalid():
    config = load_config([DATA_DIR / "invalid.toml"])

    # Only default build environment available
    assert DEFAULT_BUILD_ENVIRONMENT in config.environments
    assert len(config.environments) == 1


def test_load_config_defaults():
    config = load_config([DATA_DIR / "defaults.toml"])

    assert config.environments["tst"].exonet_project_name == "default-project"
    assert config.environments["tst"].docker_repo == "default-project"
    assert config.environments["tst"].slack_channel == "default-project"
