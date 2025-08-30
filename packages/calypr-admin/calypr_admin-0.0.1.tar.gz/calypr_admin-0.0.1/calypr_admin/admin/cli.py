import logging
import sys
from collections import defaultdict
from typing import Any

import click
from gen3.auth import Gen3AuthError

from calypr_admin import NaturalOrderGroup, Config
from calypr_admin.admin.collaborator.cli import collaborator_group
from calypr_admin.admin.gen3.buckets import get_buckets
from calypr_admin.admin.projects.cli import project_group as project
from calypr_admin.common import common_options, CLIOutput, INFO_COLOR
from calypr_admin.config import ensure_config, ensure_auth

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__package__)


@click.group(cls=NaturalOrderGroup)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context):
    """A CLI for managing Calypr projects."""
    pass


@cli.command(name="ping")
@common_options(skip_project_id=True)
@click.pass_context
def ping(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
):
    """Verify and test connectivity."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        msgs = []
        if not config.gen3.profile:
            msgs.append("no profile specified")
            output.update({"msg": "Configuration ERROR: " + ", ".join(msgs)})
            output.exit_code = 1
            return
        auth = None
        ok = True
        try:
            print(f"Using profile {config.gen3.profile}", file=sys.stderr)
            auth = ensure_auth(config=config, validate=True)
            assert auth, "Authentication failed"
            msgs.append(f"Connected using profile:{config.gen3.profile}")
        except (AssertionError, ValueError) as e:
            msgs.append(str(e))
            ok = False
        except Gen3AuthError as e:
            msg = str(e).split(":")[0]
            msgs.append(msg)
            msg2 = str(e).split('<p class="introduction">')[-1]
            msg2 = msg2.split("</p>")[0]
            msgs.append(msg2)
            ok = False

        if ok:
            _ = "Configuration OK: "
        else:
            _ = "Configuration ERROR: "
            output.exit_code = 1

        _ = {"msg": _ + ", ".join(msgs)}
        if auth:
            _["endpoint"] = auth.endpoint
            user_info = auth.curl("/user/user").json()
            _["username"] = user_info["username"]
            buckets = get_buckets(auth)
            bucket_info: dict[str, Any] = {}
            program_info = defaultdict(list)
            for k, v in buckets["S3_BUCKETS"].items():
                bucket_info[k] = {}
                if "programs" not in v:
                    bucket_info[k] = "No `programs` found"
                    click.secho(
                        f"WARNING: No `programs` found for bucket {k}",
                        fg=INFO_COLOR,
                        file=sys.stderr,
                    )
                    continue
                bucket_info[k] = ",".join(v["programs"])
                for program in v["programs"]:
                    program_info[program].append(k)
            _["bucket_programs"] = bucket_info

            for k, v in program_info.items():
                if len(v) > 1:
                    click.secho(
                        f"WARNING: {k} is in multiple buckets: {', '.join(v)}",
                        fg=INFO_COLOR,
                        file=sys.stderr,
                    )

            assert "authz" in user_info, "No authz found"
            authz_info = defaultdict(dict)

            for k, v in user_info["authz"].items():
                authz_info[k] = ",".join(set([_["method"] for _ in v]))
            _["your_access"] = dict(authz_info)

        output.update(_)


cli.add_command(project)
cli.add_command(collaborator_group)


if __name__ == "__main__":
    cli()
