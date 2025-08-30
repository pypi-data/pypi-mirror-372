import sys

import click

from calypr_admin.admin.gen3.buckets.cli import bucket_group
from calypr_admin.admin.projects.adder import initialize_project_server_side
from calypr_admin.common import common_options
from calypr_admin.common import CLIOutput
from calypr_admin.config import Config, ensure_auth, ensure_config
from calypr_admin.admin.projects.lister import ls
from calypr_admin.admin.projects.remover import empty
from calypr_admin import NaturalOrderGroup


@click.group(name="projects", cls=NaturalOrderGroup)
@click.pass_context
def project_group(ctx: click.Context):
    """Manage Gen3 projects."""
    pass


@project_group.command(name="ls")
@common_options(skip_project_id=True)
@click.pass_context
def project_ls(
    ctx: click.Context, output_format: str, profile: str, debug: bool, dry_run: bool
):
    """List all projects user has access to."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        try:
            auth = ensure_auth(config=config)
            output.update(ls(config, auth=auth))
        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


@project_group.command(name="add")
@click.option(
    "--force",
    default=False,
    show_default=True,
    is_flag=True,
    help="Force project creation even if existing requests found",
)
@common_options
@click.pass_context
def project_add(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    force: bool,
):
    """Create a new project, adding necessary policies server side."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        try:
            logs, approval_needed = initialize_project_server_side(
                config=config, project_id=project_id, force=force
            )
            if logs:
                output.update({"logs": logs})
            if approval_needed:
                output.update(
                    {"msg": f"Project {project_id} creation pending admin approval"}
                )
        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


@project_group.command(name="empty")
@click.option(
    "--confirm", default=None, show_default=True, help="Enter 'empty' to confirm"
)
@common_options
@click.pass_context
def project_empty(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str | None,
    confirm: str,
):
    """Empty all metadata (graph, flat) for a project."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        try:
            assert confirm == "empty", "Please confirm by entering --confirm empty"
            if not project_id:
                project_id = config.gen3.project_id
                click.secho(
                    f"No project_id provided, using current project {project_id}",
                    fg="yellow",
                    file=sys.stderr,
                )
            _ = empty(config, project_id)
            _["msg"] = f"Emptied {project_id}"
            output.update(_)
        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


project_group.add_command(bucket_group)

# @project_group.command(name="bucket")
# @common_options
# @click.pass_context
# def project_bucket(
#     ctx: click.Context,
#     project_id: str,
#     output_format: str,
#     profile: str,
#     debug: bool,
#     dry_run: bool,
# ):
#     """Show project bucket."""
#     ensure_config(ctx, output_format, profile, debug, dry_run)
#     config: Config = ctx.obj
#
#     if not project_id:
#         project_id = config.gen3.project_id
#         click.secho(
#             f"No project_id provided, using current project {project_id}",
#             fg="yellow",
#             file=sys.stderr,
#         )
#     with CLIOutput(config=config) as output:
#         try:
#             if not project_id or "-" not in project_id:
#                 raise ValueError(f"Invalid project_id: {project_id}")
#             program, project = project_id.split("-")
#             buckets = get_buckets(config=config)
#             for k, v in buckets["S3_BUCKETS"].items():
#                 assert (
#                     "programs" in v
#                 ), f"no configured programs in fence buckets {v} {buckets}"
#                 if program in v["programs"]:
#                     output.update({k: v})
#         except Exception as e:
#             output.update({"msg": str(e)})
#             output.exit_code = 1
#             if config.debug:
#                 raise e
