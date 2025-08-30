import gzip
import io
import json
import logging
import pathlib
from datetime import datetime
from typing import Mapping, Iterator

import click
import orjson
import yaml
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

from calypr_admin import Config, ENV_VARIABLE_PREFIX

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__package__)

# Define color constants
INFO_COLOR = "yellow"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"

PROJECT_DIR = ".g3t"
PROJECT_DIRECTORIES = [PROJECT_DIR, "META/", "MANIFEST/", "logs/"]
PROJECT_README = """
# Data Directory

Welcome to the data directory! This repository contains important data files for our project. Before you proceed, please take note of the following guidelines to ensure the security and integrity of our data.

## Important Note: Do Not Check in Protected Files

Some files in this directory are considered protected and contain sensitive information.

**DO NOT** check in or commit these protected files to the version control system (e.g., Git).

This is crucial to prevent unauthorized access and to comply with security and privacy policies.


## Usage Guidelines:

1. **Read-Only Access:** Unless you have explicit permission to modify or update the data, treat this directory as read-only.

2. **Data Integrity:** Ensure the integrity of the data by following proper procedures for reading, updating, and managing files.

3. **Security Awareness:** Be aware of the sensitivity of the data stored here and take necessary precautions to protect it from unauthorized access.


Thank you for your cooperation in maintaining the security and confidentiality of our data.
"""


# def _default_json_serializer(obj):
#     """JSON Serializer, render decimal and bytes types."""
#     if isinstance(obj, decimal.Decimal):
#         return float(obj)
#     if isinstance(obj, bytes):
#         return obj.decode()
#     raise TypeError


def print_formatted(config, output: Mapping) -> None:
    """Print the output, using configured output format"""
    from calypr_admin import Config

    config: Config = config
    if config.output.format == "yaml":
        print(yaml.dump(output, sort_keys=False))
    elif config.output.format == "json":
        print(
            orjson.dumps(
                output, default=pydantic_encoder, option=orjson.OPT_INDENT_2
            ).decode()
        )
    else:
        print(output)


def read_ndjson_file(path: str) -> Iterator[dict]:
    """Read ndjson file, load json line by line."""
    with _file_opener(path) as jsonfile:
        for l_ in jsonfile.readlines():
            yield orjson.loads(l_)


# def read_json_file(path: str) -> Iterator[dict]:
#     """Read ndjson file, load json line by line."""
#     with _file_opener(path) as jsonfile:
#         try:
#             yield orjson.loads(jsonfile.read())
#         except orjson.JSONDecodeError as e:
#             logging.error(f"Error reading {path}: {e}")
#             raise


# def read_yaml(path: str) -> Dict:
#     """Read a yaml file."""
#     with open(path, "r") as fp:
#         return yaml.safe_load(fp.read())


# def is_url(to_) -> bool:
#     """Does the destination parameter describe an upload? ie have an url.scheme"""
#     return len(urlparse(to_).scheme) > 0


# def is_json_extension(name: str) -> bool:
#     """Files we are interested in"""
#     if name.endswith("json.gz"):
#         return True
#     if name.endswith("json"):
#         return True
#     return False


# def is_ndjson(file_path: pathlib.Path) -> bool:
#     """Open file, check if ndjson."""
#     fp = _file_opener(file_path)
#     try:
#         with fp:
#             for line in fp.readlines():
#                 orjson.loads(line)
#                 break
#         return True
#     except Exception as e:  # noqa
#         return False


def _file_opener(file_path):
    """Open file appropriately."""
    if isinstance(file_path, str):
        file_path = pathlib.Path(file_path)
    if file_path.name.endswith("gz"):
        fp = io.TextIOWrapper(io.BufferedReader(gzip.GzipFile(file_path)))  # noqa
    else:
        fp = open(file_path, "rb")
    return fp


def validate_email(email) -> list[str]:
    """Ensure that the email is valid"""
    msgs = []
    if not email:
        msgs.append("email is missing")
    if not email.count("@") == 1:
        msgs.append(f"{email} should have a single '@' delimiter.")
    try:
        from email_validator import (
            validate_email as email_validator_validate,
            EmailNotValidError,
        )

        email_validator_validate(email)
    except EmailNotValidError as e:
        msgs.append(f"{email} is not a valid email address. {e}")
    return msgs


def to_resource_path(project_id):
    """Canonical conversion of project_id to resource path."""
    if "-" not in project_id:
        return project_id
    _ = project_id.split("-")
    return f"/programs/{_[0]}/projects/{_[1]}"


class Commit(BaseModel):
    """A commit."""

    commit_id: str = None
    """The commit id."""
    object_id: str = None
    """The metadata file object_id."""
    message: str = None
    """The commit message."""
    resource_counts: dict = None
    """The resource counts of meta in this commit."""
    exceptions: list = None
    """The exceptions."""
    logs: list = None
    """The logs."""
    path: pathlib.Path = None
    """The path to the commit directory."""
    manifest_sqlite_path: pathlib.Path = None
    """The path to the manifest file."""
    meta_path: pathlib.Path = None
    """The path to the meta zip file."""


class Push(BaseModel):
    """A list of commits."""

    config: Config
    """The config."""

    commits: list[Commit] = []
    """A list of commits in this push."""

    published_timestamp: datetime = None
    """When the push was published."""

    published_job: dict = None

    def model_dump(self):
        """Dump the model.

        temporary until we switch to pydantic2
        """
        _ = self.model_dump_json(exclude={"config"})
        return json.loads(_)

    def pending_meta_index(self) -> list[dict]:
        """Index of pending meta files {id: resourceType}."""
        commits_dir = self.config.state_dir / self.config.gen3.project_id / "commits"
        pending_path = commits_dir / "pending.ndjson"
        pending = []
        if not pending_path.exists():
            return pending
        for _ in read_ndjson_file(pending_path):
            with open(commits_dir / _["commit_id"] / "meta-index.ndjson") as fp:
                for line in fp.readlines():
                    pending.append(orjson.loads(line))
        return pending


# def dict_md5(resource: dict) -> str:
#     """Return the md5 of the dict."""
#     return md5(orjson.dumps(resource, option=orjson.OPT_SORT_KEYS)).hexdigest()


class CommandOutput(object):
    """Output object for commands."""

    def __init__(self):
        self.obj = None
        self.exit_code = 0

    def update(self, obj):
        """Update output with obj."""
        self.obj = obj


class CLIOutput:
    """Ensure output, exceptions and exit code are returned to user consistently."""

    from calypr_admin import Config

    def __init__(self, config: Config, exit_on_error: bool = True):
        self.output = CommandOutput()
        self.config = config
        self.exit_on_error = exit_on_error

    def __enter__(self):
        return self.output

    def __exit__(self, exc_type, exc_val, exc_tb):
        rc = 0
        _ = {}
        if self.output.obj is not None:
            if isinstance(self.output.obj, dict):
                _.update(self.output.obj)
            elif isinstance(self.output.obj, list):
                _ = self.output.obj
            elif isinstance(self.output.obj, int):
                _ = {"count": self.output.obj}
            elif hasattr(self.output.obj, "model_dump"):
                _.update(self.output.obj.model_dump())
            else:
                _.update(self.output.obj.model_dump())
        rc = self.output.exit_code
        if exc_type is not None:
            if isinstance(self.output.obj, dict):
                _["exception"] = f"{str(exc_val)}"
            elif isinstance(self.output.obj, list):
                _.append(f"{str(exc_val)}")
            else:
                _.update({"exception": f"{str(exc_val)}"})
            rc = 1
            logging.getLogger(__name__).exception(exc_val)
        if isinstance(_, dict) and "msg" not in _:
            if rc == 1:
                _["msg"] = "FAIL"
            else:
                _["msg"] = "OK"
        prune = []
        if isinstance(_, dict):
            for k, v in _.items():
                if not v:
                    prune.append(k)
            for k in prune:
                del _[k]
        print_formatted(self.config, _)
        self.output.exit_code = rc
        if rc != 0 and self.exit_on_error:
            exit(rc)


# def parse_iso_tz_date(date_str: str) -> str:
#     """Parse an iso date string."""
#     # parse the string into a datetime object
#     date_obj = dateutil_parser.parse(date_str)
#     # if the date string doesn't have a timezone, you can add one
#     if date_obj.tzinfo is None:
#         date_obj = date_obj.replace(tzinfo=tzutc())
#     # convert the datetime object back into an ISO formatted string with timezone
#     return date_obj.isoformat()


def validate_project_id_callback(ctx, param, value):
    """Validate project_id callback for click."""
    if value is None:
        return value
    if value.count("-") != 1:
        raise click.BadParameter("project_id should have a single '-' delimiter.")
    return value


def common_options(func=None, *, skip_project_id: bool = False):
    """Common options for all commands."""

    def decorator(f):
        f = click.option(
            "--profile",
            "profile",
            envvar=f"{ENV_VARIABLE_PREFIX}PROFILE",
            default=None,
            show_default=True,
            help=f"Connection name. {ENV_VARIABLE_PREFIX}PROFILE See https://bit.ly/3NbKGi4",
        )(f)
        if not skip_project_id:
            f = click.option(
                "--project_id",
                default=None,
                show_default=True,
                help="Gen3 program-project",
                envvar=f"{ENV_VARIABLE_PREFIX}PROJECT_ID",
                callback=validate_project_id_callback,
            )(f)
        f = click.option(
            "--format",
            "output_format",
            envvar=f"{ENV_VARIABLE_PREFIX}FORMAT",
            default="yaml",
            show_default=True,
            type=click.Choice(["yaml", "json", "text"], case_sensitive=False),
            help=f"Result format. {ENV_VARIABLE_PREFIX}FORMAT",
        )(f)
        f = click.option("--debug", is_flag=True, help="Enable debug mode")(f)
        f = click.option("--dry-run", is_flag=True, help="Dry run")(f)
        return f

    if func is None:
        return decorator
    return decorator(func)
