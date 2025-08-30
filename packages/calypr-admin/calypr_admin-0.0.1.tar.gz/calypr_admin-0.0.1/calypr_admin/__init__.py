import json
import pathlib
from collections import OrderedDict

import click
from pydantic import BaseModel

ENV_VARIABLE_PREFIX = "CALYPR_"


class LogConfig(BaseModel):
    format: str
    """https://docs.python.org/3/library/logging.html#logging.Formatter"""
    level: str
    """https://docs.python.org/3/library/logging.html#logging-levels"""


class OutputConfig(BaseModel):
    format: str = "text"
    """write to stdout with this format"""


# class _DataclassConfig:
#     """Pydantic dataclass configuration
#
#     See https://docs.pydantic.dev/latest/usage/model_config/#options"""
#
#     arbitrary_types_allowed = True


class Gen3Config(BaseModel):

    profile: str | None = None
    """The name of the gen3-client profile in use. See https://bit.ly/3NbKGi4"""

    project_id: str | None = None
    """The program-project."""

    @property
    def program(self) -> str | None:
        if not self.project_id:
            return None
        return self.project_id.split("-")[0]

    @property
    def project(self) -> str | None:
        if not self.project_id:
            return None
        return self.project_id.split("-")[1]


class Config(BaseModel):
    log: LogConfig = LogConfig(
        format="[%(asctime)s] — [%(levelname)s] — %(name)s — %(message)s", level="INFO"
    )
    """logging setup"""
    output: OutputConfig = OutputConfig(format="yaml")
    """output setup"""
    gen3: Gen3Config = Gen3Config()
    """gen3 setup"""
    work_dir: pathlib.Path = None
    """temporary files"""
    no_config_found: bool = False
    """DEPRECATED Is this default config used because none found in cwd or parents?"""
    debug: bool = False
    """Enable debug mode, lots of logs."""
    dry_run: bool = False
    """Print the commands that would be executed, but do not execute them."""

    def model_dump(self):
        """Dump the config model.

        temporary until we switch to pydantic2
        """
        _ = json.loads(self.model_dump_json())
        del _["no_config_found"]
        return _


# cli helpers -------------------------------------------------------------------
class NaturalOrderGroup(click.Group):
    """Allow listing Commands in order of appearance, with common parameters."""

    # see https://github.com/pallets/click/issues/513

    def __init__(self, name=None, commands=None, **attrs):
        if commands is None:
            commands = OrderedDict()
        elif not isinstance(commands, OrderedDict):
            commands = OrderedDict(commands)
        click.Group.__init__(self, name=name, commands=commands, **attrs)

    def list_commands(self, ctx):
        """List command names as they are in commands dict.

        If the dict is OrderedDict, it will preserve the order commands
        were added.
        """
        return self.commands.keys()
