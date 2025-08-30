import importlib.resources as pkg_resources
import logging
import os
import pathlib
import sys
from configparser import ConfigParser
from datetime import datetime, timezone, timedelta

import click
import jwt
import requests
import yaml
from gen3.auth import Gen3Auth

import calypr_admin
from calypr_admin import Config

_logger = logging.getLogger(__name__)


def gen_client_ini_path() -> pathlib.Path:
    """Return path to gen3-client ini file. See https://bit.ly/3NbKGi4"""
    path = pathlib.Path(pathlib.Path.home() / ".gen3" / "gen3_client_config.ini")
    if not path.is_file():
        raise FileNotFoundError(
            f"gen3-client ini file not found {path}, see https://bit.ly/3NbKGi4"
        )
    return path


def gen3_client_profiles(path: str = None) -> list[str]:
    """Read gen3-client ini file, return list of profiles."""
    if not path:
        path = gen_client_ini_path().absolute()
    gen3_util_ini = read_ini(path)
    return gen3_util_ini.sections()


def read_ini(path: str):
    """Read ini file."""
    import configparser
    import pathlib

    path = pathlib.Path(path)
    assert path.is_file(), f"{path} is not a file"
    _ = configparser.ConfigParser()
    _.read(path)
    return _


def write_ini(path: str, config: ConfigParser):
    """Write ini file."""
    with open(path, "w") as configfile:
        config.write(configfile)


def key_expired_msg(api_key, expiration_threshold_days, key_name):
    """Confirm that api_key is not expired."""
    key = jwt.decode(api_key, options={"verify_signature": False})
    now = datetime.now(tz=timezone.utc).timestamp()
    msg = "OK, key is valid"
    exp_str = datetime.fromtimestamp(key["exp"], tz=timezone.utc).isoformat()
    iat_str = datetime.fromtimestamp(key["iat"], tz=timezone.utc).isoformat()
    now_str = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
    if key["exp"] < now:
        msg = f"ERROR key for {key_name} expired {exp_str} < {now_str}"
    if key["iat"] > now:
        msg = f"ERROR key for {key_name} not yet valid {iat_str} > {now_str}"
    delta = timedelta(seconds=key["exp"] - now)
    if 0 < delta.days < expiration_threshold_days:
        msg = f"WARNING {key_name}: Key will expire in {delta.days} days, on {exp_str}"
    return msg


def _get_gen3_client_default_profile(
    path: pathlib.Path | None = None, gen3_util_ini: ConfigParser | None = None
) -> str | None:
    """Read gen3-client ini file, return default (only) profile."""
    if gen3_util_ini is None:
        assert path, "path is required"
        gen3_util_ini = read_ini(path)
    if len(gen3_util_ini.sections()) == 1:
        # default to first section if only one section
        profile = gen3_util_ini.sections()[0]
        return profile
    return None


def _get_gen3_client_key(path: pathlib.Path, profile: str = None) -> str | None:
    """Read gen3-client ini file, return api_key for profile."""

    gen3_util_ini = read_ini(str(path))

    if profile:
        for section in gen3_util_ini.sections():
            if section == profile:
                return gen3_util_ini[section]["api_key"]
    else:
        profile = _get_gen3_client_default_profile(gen3_util_ini=gen3_util_ini)
        if profile:
            return gen3_util_ini[profile]["api_key"]
    click.secho(
        f"no profile '{profile}' found in {path}, specify one of {gen3_util_ini.sections()}, optionally set environmental variable: GEN3_UTIL_PROFILE",
        fg="yellow",
    )
    return None


def ensure_auth(
    refresh_file: [pathlib.Path, str] = None,
    validate: bool = False,
    config: Config = None,
) -> Gen3Auth:
    """Confirm connection to Gen3 using their conventions.

    Args:
        refresh_file (pathlib.Path): The file containing the downloaded JSON web token.
        validate: check the connection by getting a new token
        config: Config

    """

    try:
        if refresh_file:
            if isinstance(refresh_file, str):
                refresh_file = pathlib.Path(refresh_file)
            auth = Gen3Auth(refresh_file=refresh_file.name)
        elif "ACCESS_TOKEN" in os.environ:
            auth = Gen3Auth(refresh_file=f"accesstoken:///{os.getenv('ACCESS_TOKEN')}")
        elif gen_client_ini_path().exists():
            profile = config.gen3.profile
            if not profile:
                # in disconnected mode, or not in project dir
                if config.no_config_found:
                    print(
                        "INFO: No config file found in current directory or parents.",
                        file=sys.stderr,
                    )
                return None
            # https://github.com/uc-cdis/gen3sdk-python/blob/master/gen3/auth.py#L190-L191
            key = _get_gen3_client_key(gen_client_ini_path(), profile=profile)
            if not key:
                print(
                    f"ERROR: No api_key found for profile '{profile}' in {gen_client_ini_path()}",
                    file=sys.stderr,
                )
                raise ValueError(
                    f"ERROR: No api_key found for profile '{profile}' in {gen_client_ini_path()}"
                )
            msg = key_expired_msg(key, key_name=profile, expiration_threshold_days=10)
            if "ERROR" in msg:
                raise ValueError(msg.replace("ERROR", ""))  # remove ERROR prefix
            if "WARNING" in msg:
                print(msg, file=sys.stderr)
            auth = Gen3Auth(
                refresh_token={
                    "api_key": key,
                }
            )
        else:
            auth = Gen3Auth()

        if validate:
            api_key = auth.refresh_access_token()
            assert api_key, "refresh_access_token failed"

    except (requests.exceptions.ConnectionError, AssertionError) as e:
        msg = (
            f"Could not get access. profile={profile}"
            "See https://bit.ly/3NbKGi4, "
            f"{e}"
        )

        logging.getLogger(__name__).error(msg)
        raise AssertionError(msg)

    return auth


def default():
    """Load config from directory or installed package."""

    # use default

    # different pkg_resources open for 3.9
    if sys.version_info[:3] <= (3, 9):
        _config = Config(
            **yaml.safe_load(
                pkg_resources.open_text(calypr_admin, "config.yaml").read()
            )
        )
    else:
        # https://docs.python.org/3.11/library/importlib.resources.html#importlib.resources.open_text
        _config = Config(
            **yaml.safe_load(
                pkg_resources.files(calypr_admin).joinpath("config.yaml").open().read()
            )
        )

    return _config


def ensure_config(
    ctx: click.Context, output_format: str, profile: str, debug: bool, dry_run: bool
):
    """Ensure that ctx.obj is a Config object."""
    # load config
    config__ = calypr_admin.config.default()
    logging.basicConfig(
        format=config__.log.format, level=config__.log.level, stream=sys.stderr
    )

    if output_format:
        config__.output.format = output_format

    try:
        # _profiles = gen3_client_profiles()

        if profile:
            # if profile not in _profiles:
            #     click.secho(
            #         f"Profile {profile} not found. Existing profiles {_profiles}",
            #         fg="red",
            #     )
            #     exit(1)
            config__.gen3.profile = profile
            # elif not config__.gen3.profile:
            #     if not _profiles:
            #         click.secho("No gen3_client profile found.", fg="red")
            #         exit(1)
            #     else:
            #         if len(_profiles) > 1:
            #             click.secho(
            #                 f"WARNING: No --profile specified, found multiple gen3_client profiles: {_profiles}",
            #                 fg="red",
            #             )
            #         else:
            #             click.secho(
            #                 f"Using default gen3_client profile {_profiles[0]}", fg="yellow"
            #             )
            #             config__.gen3.profile = _profiles[0]
    except Exception as e:
        _logger.warning(f"Error loading gen3_client profiles: {e}")
        click.secho(
            "Warning: Error loading gen3_client profiles. Please check your gen3_client configuration.",
            fg="red",
        )
        config__.gen3.profile = "PROFILE_NOT_FOUND"

    # ensure that ctx.obj exists
    config__.debug = debug
    config__.dry_run = dry_run

    ctx.obj = config__

    if debug:
        _logger.setLevel(logging.DEBUG)
