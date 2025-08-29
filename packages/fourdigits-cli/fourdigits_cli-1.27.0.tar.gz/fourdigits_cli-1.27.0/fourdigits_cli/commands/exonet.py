import logging
import os
import tempfile
from contextlib import contextmanager

import click
import requests
from exonetapi import Client
from exonetapi.structures import ApiResource, ApiResourceIdentifier
from fabric import Connection
from fabric.transfer import Transfer

from fourdigits_cli.settings import (
    DEFAULT_BUILD_ENVIRONMENT,
    DEFAULT_CONFIG,
    get_environment_config,
)
from fourdigits_cli.utils.docker import Docker

logger = logging.getLogger(__name__)

DRONE_BUILD_URL = os.getenv(
    "DRONE_BUILD_URL",
    "https://drone.exonet.nl/api/repos/exonet/containers-fourdigits/builds",
)
DRONE_JOB_ID = "1715"

MINIO_HOSTNAME = "fd-cdn.nl"


@click.group()
def group():
    pass


@group.command()
@click.argument("environment")
@click.argument("docker_tag")
@click.option("--message", default="", show_default=True)
@click.option("--name", default="", show_default=True)
@click.option("--drone-job-id", default=DRONE_JOB_ID, show_default=True)
@click.option("--drone_token", default="", show_default=True)
def deploy(
    environment, docker_tag, message="", name="", drone_job_id="", drone_token=""
):
    config = get_environment_config(environment)
    drone_job_id = os.getenv("DRONE_JOB_ID", "") or drone_job_id
    drone_token = drone_token or os.getenv("DRONE_TOKEN", "")
    name = name or config.exonet_project_name

    if not drone_token:
        raise click.ClickException(
            "Environment variable DRONE_TOKEN is not set. "
            "Get it from https://drone.exonet.nl/account/token. "
            "Alternatively, you can pass it as the --drone_token argument."
        )

    if not name:
        raise click.ClickException(
            "No name found. You can supply this by settings the exonet_project_name "
            "in pyproject.toml. Alternatively, you can pass it as the --name argument."
        )

    if not message:
        message = f"[{name}] Deploying {docker_tag} to {config.exonet_environment} environment"  # noqa: E501

    response = requests.post(
        url=DRONE_BUILD_URL,
        headers={
            "Authorization": f"Bearer {drone_token}",
        },
        params={
            "job_id": drone_job_id,
            "name": name,
            "target": config.exonet_environment,
            "tag": docker_tag,
            "channel": config.slack_channel,
            "message": message,
        },
    )

    if response.status_code != 200:
        raise click.ClickException(response.text)
    click.echo(response.text)


@group.command(name="db:download")
@click.argument("environment")
def db_download(environment):
    """
    Download database from Exonet container-db01 server
    and import it into the docker-compose database or local database.

    It will use the project name in the pyproject.toml for the database name.

    If a docker-compose.yml file is found, it will import the database into the
    docker-compose database (wil use service name: db).
    Otherwise, it will import it into the local database (localhost:5432).
    """
    config = get_environment_config(environment)

    username = f"{config.exonet_project_name}_{config.exonet_environment}"
    db_password_filename = f"db-password-{username}"
    db_dump_filename = f"{username}.psql"
    connection = Connection(config.database_ssh_username)
    transfer = Transfer(connection)
    click.echo(f"Copy database password from docker01 to db01 ({db_password_filename})")
    with get_db_password_file(
        connection, username, config.application_ssh_host
    ) as db_password_filename:
        click.echo(f"Download database for {username}")
        run_pg_dump(
            connection,
            db_password_filename,
            username,
            config.database_host,
            db_dump_filename,
        )

    click.echo(f"Dumped database to {db_dump_filename} on server, downloading")
    transfer.get(db_dump_filename)
    connection.run(f"rm {db_dump_filename}")
    click.echo(f"Downloaded and removed {db_dump_filename} from server")

    default_docker_compose_filenames = [
        "docker-compose.yml",  # the default for Four Digits cookiecutter projects
        "compose.yaml",
        "compose.yml",
        "docker-compose.yaml",
    ]
    if any(
        os.path.exists(os.path.join(os.getcwd(), filename))
        for filename in default_docker_compose_filenames
    ):
        click.echo("Importing into docker database")
        docker = Docker()
        docker.compose("up", "db", "--detach", "--wait")
        docker.compose("cp", db_dump_filename, f"db:{db_dump_filename}")
        docker.compose(
            "exec",
            "-it",
            "db",
            "psql",
            f"--username={config.name}",
            config.name,
            "--file",
            db_dump_filename,
        )
        click.echo(f"Imported {db_dump_filename} into docker database")
    else:
        click.echo("Importing into local (non-Docker) database")
        os.system(f"dropdb {config.name}")
        os.system(f"createdb {config.name}")
        os.system(f"psql {config.name} --file {db_dump_filename}")
        click.echo(f"Imported {db_dump_filename} into local database")

    os.remove(db_dump_filename)
    click.echo(f"Removed {db_dump_filename}")


@group.command(name="db:copy")
@click.argument("from_environment")
@click.argument("to_environment")
def db_copy(from_environment, to_environment):
    """
    Copy database from one environment to another.
    """
    from_config = get_environment_config(from_environment)
    to_config = get_environment_config(to_environment)

    if from_environment == to_environment:
        raise click.ClickException("Can't copy to the same environment")
    if to_environment == "prd":
        click.confirm("Are you sure you want to overwrite prd?", abort=True)
        click.confirm("Really really sure?", abort=True)

    from_username = (
        f"{from_config.exonet_project_name}_{from_config.exonet_environment}"
    )
    to_username = f"{to_config.exonet_project_name}_{to_config.exonet_environment}"
    db_dump_filename = f"{from_username}.psql"
    db_connection = Connection(to_config.database_ssh_username)
    try:
        with get_db_password_file(
            db_connection, from_username, from_config.application_ssh_host
        ) as from_db_password_filename:
            click.echo(f"Dumping database for {from_username}")
            run_pg_dump(
                db_connection,
                from_db_password_filename,
                from_username,
                to_config.database_host,
                db_dump_filename,
            )

        with get_db_password_file(
            db_connection, to_username, to_config.application_ssh_host
        ) as to_db_password_filename:
            run_psql(
                db_connection,
                to_db_password_filename,
                to_username,
                to_config.database_host,
                '--command "DROP SCHEMA public CASCADE"',
            )
            run_psql(
                db_connection,
                to_db_password_filename,
                to_username,
                to_config.database_host,
                '--command "CREATE SCHEMA public"',
            )
            click.echo(f"Importing database for {to_username}")
            run_psql(
                db_connection,
                to_db_password_filename,
                to_username,
                to_config.database_host,
                f"--file {db_dump_filename}",
            )
    finally:
        db_connection.run(f"rm {db_dump_filename}")
        click.echo(f"Removed {db_dump_filename} from server")


@group.command(name="minio:create")
@click.argument("environments", nargs=-1)
@click.option("--refresh-access-token", is_flag=True, default=False)
@click.option("--name", default="", show_default=True)
@click.option("--token", default="", show_default=True)
def minio_create(environments, refresh_access_token=False, name="", token=""):
    """Create minio user/buckets/access token if not exists."""
    environments = list(
        environments
        or [
            env
            for env in DEFAULT_CONFIG.environments.keys()
            if env != DEFAULT_BUILD_ENVIRONMENT
        ]
    )

    if not environments:
        raise click.ClickException(
            "No environments specified or found in pyproject.toml"
        )

    name = name or get_environment_config(environments[0]).exonet_project_name
    token = token or os.getenv("EXONET_API_TOKEN", "")

    if not token:
        raise click.ClickException(
            "Environment variable EXONET_API_TOKEN is not set. "
            "Get it from 1Password. Alternatively, "
            "you can pass it as the --token argument."
        )

    if not name:
        raise click.ClickException(
            "No name found. You can supply this by settings the exonet_project_name "
            "in pyproject.toml. Alternatively, you can pass it as the --name argument."
        )

    client = Client("https://api.exonet.nl")
    client.authenticator.set_token(token)

    # Four digits account should only have one customer and storage instance?
    customer = client.resource("customers").get().resources()[0]
    storage_instance = client.resource("object_storage_instances").get().resources()[0]

    # User
    storage_user = get_resource_by_name(client, "object_storage_users", name)
    if not storage_user:
        storage_user = ApiResource("object_storage_users")
        storage_user.attribute("name", name)
        storage_user.attribute("wildcard_bucket_policy", False)
        storage_user.relationship(
            "customer", ApiResourceIdentifier("customers", customer.id())
        )
        storage_user.relationship(
            "object_storage_instance",
            ApiResourceIdentifier("object_storage_instances", storage_instance.id()),
        )
        storage_user = storage_user.post()

    # Buckets
    storage_buckets = []
    for env in environments:
        bucket_name = f"{name}-{env}"
        storage_bucket = get_resource_by_name(
            client, "object_storage_buckets", bucket_name
        )
        if not storage_bucket:
            storage_bucket = ApiResource("object_storage_buckets")
            storage_bucket.attribute("name", bucket_name)
            # Versioning must be enabled — it provides backup-like functionality
            # similar to how traditional filesystems use backup scripts for
            # recovery.
            storage_bucket.attribute("versioning", True)
            storage_bucket.attribute("encryption", False)
            storage_bucket.relationship(
                "customer", ApiResourceIdentifier("customers", customer.id())
            )
            storage_bucket.relationship(
                "object_storage_instance",
                ApiResourceIdentifier(
                    "object_storage_instances", storage_instance.id()
                ),
            )
            storage_bucket.relationship(
                "object_storage_user",
                ApiResourceIdentifier("object_storage_users", storage_user.id()),
            )
            storage_bucket = storage_bucket.post()
        storage_buckets.append(storage_bucket)

    # Access token
    access_token = get_resource_by_name(client, "object_storage_access_keys", name)
    if access_token and refresh_access_token:
        access_token.delete()
        access_token = None

    if not access_token:
        access_token = ApiResource("object_storage_access_keys")
        access_token.attribute("name", name)
        access_token.relationship(
            "object_storage_user",
            ApiResourceIdentifier("object_storage_users", storage_user.id()),
        )
        access_token = access_token.post()

    # Show console access
    click.echo(click.style("--- Console access ---", bold=True))
    click.echo("URl: https://shared-console.s3.exonet.io")
    click.echo(f"Username: {storage_user.attribute('username')}")
    if storage_user.attribute("password"):
        click.echo(
            f"Password: {storage_user.attribute('password')} (This will be shown only once, save it securely)"  # noqa: E501
        )
    else:
        click.echo("Password: ******** (User was already created)")
    click.echo()
    # Show bucket access
    click.echo(click.style("--- Bucket access ---", bold=True))
    click.echo(f"URl: https://{MINIO_HOSTNAME}/")
    click.echo(f"Access key: {access_token.attribute('access_key')}")
    if access_token.attribute("secret_key"):
        click.echo(
            f"Secret key: {access_token.attribute('secret_key')} (This will be shown only once, save it securely)"  # noqa: E501
        )
    else:
        click.echo("Secret key: ******** (Token was already created)")
    click.echo()
    # Show buckets
    click.echo(click.style("--- Buckets ---", bold=True))
    for bucket in storage_buckets:
        click.echo(f"{bucket.attribute('object_storage_name')}")
    click.echo()
    click.echo(
        "Note: Policies are not set automatically, Please create a ticket at https://portal.exonet.nl/klanten/tickets to request a policy that makes the static and media directories publicly accessible."  # noqa: E501
    )


@group.command(name="minio:list")
@click.option("--token", default="", show_default=True)
def minio_list(token=""):
    """List all minio buckets"""

    token = token or os.getenv("EXONET_API_TOKEN", "")
    if not token:
        raise click.ClickException(
            "Environment variable EXONET_API_TOKEN is not set. "
            "Get it from 1Password. Alternatively, "
            "you can pass it as the --token argument."
        )
    client = Client("https://api.exonet.nl")
    client.authenticator.set_token(token)

    for obj in client.resource("object_storage_buckets").sort("name").get_recursive():
        name = obj.attribute("name")
        bucket_name = obj.attribute("object_storage_name")
        click.echo(f"{bucket_name} ({name}[{obj.id()}])")


def get_resource_by_name(client, resource, name):
    for obj in client.resource(resource).get_recursive():
        if obj.attribute("name") == name:
            return obj


@contextmanager
def get_db_password_file(db_connection, username, app_host):
    """
    Get the database password from the docker01 server and copy it to the db01 server.

    We use files to transfer the password,
    we don't want to expose the password in the command.
    """
    db_password_filename = f"db-password-{username}"
    db_transfer = Transfer(db_connection)
    click.echo(f"Copy database password from docker01 to db01 ({db_password_filename})")
    try:
        with tempfile.NamedTemporaryFile() as tmp_password_file:
            conn_docker01 = Connection(f"{username}@{app_host}")
            transfer_docker01 = Transfer(conn_docker01)
            transfer_docker01.get("secrets/db_password", tmp_password_file)
            db_transfer.put(tmp_password_file, db_password_filename)
        yield db_password_filename
    finally:
        db_connection.run(f"rm {db_password_filename}")
        click.echo(f"Removed {db_password_filename} from server")


def run_pg_dump(connection, password_filename, username, database_host, dump_filename):
    command = " ".join(
        [
            f"PGPASSWORD=$(cat {password_filename})",
            "pg_dump",
            f"--host {database_host}",
            "--port 5432",
            f"--username {username}",
            f"--dbname {username}",
            f"--clean --no-owner --no-privileges > {dump_filename}",
        ]
    )
    logger.debug(f"Running pg_dump command: {command}")
    connection.run(command)


def run_psql(connection, password_filename, username, database_host, *args):
    command = " ".join(
        [
            f"PGPASSWORD=$(cat {password_filename})",
            "psql",
            f"--host {database_host}",
            "--port 5432",
            f"--username {username}",
            f"--dbname {username}",
            *args,
        ]
    )
    logger.debug(f"Running psql command: {command}")
    connection.run(command)
