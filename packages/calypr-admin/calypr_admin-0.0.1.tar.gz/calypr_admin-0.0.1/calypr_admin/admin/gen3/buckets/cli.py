import click

from calypr_admin.admin.gen3.buckets import FenceAdminClient
from calypr_admin import NaturalOrderGroup
from calypr_admin.common import CLIOutput, common_options, to_resource_path
from calypr_admin.config import Config, ensure_auth, ensure_config


@click.group(name="buckets", cls=NaturalOrderGroup, invoke_without_command=True)
@click.pass_context
def bucket_group(ctx: click.Context):
    """Manage project buckets."""
    pass


@bucket_group.command(name="add")
@common_options
@click.option("--name", type=str, required=True, help="Name of the bucket to add")
@click.option(
    "--provider", default="s3", help="Cloud provider for the bucket (default: s3)"
)
@click.option(
    "--region", default="us-east-1", help="Region for the bucket (default: us-east-1)"
)
@click.option(
    "--endpoint", default="https://s3.amazonaws.com", help="Endpoint URL for the bucket"
)
@click.option("--auth-mode", default="iam", help="Authentication mode (default: iam)")
@click.pass_context
def add_command(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    name: str,
    provider: str,
    region: str,
    endpoint: str,
    auth_mode: str,
) -> None:
    """Add bucket to a project."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    authz = to_resource_path(project_id)

    with CLIOutput(config=config) as output:
        try:
            auth = ensure_auth(config=config, validate=True)
            output.update({"endpoint": auth.endpoint})
            output.update(
                FenceAdminClient(auth).add_bucket(
                    name=name,
                    provider=provider,
                    region=region,
                    endpoint=endpoint,
                    auth_mode=auth_mode,
                    authz=[authz],
                )
            )
        except Exception as e:
            output.update({"msg": str(e)})
            if config.debug:
                raise e
            output.exit_code = 1


@bucket_group.command(name="update")
@common_options
@click.option("--name", type=str, required=True, help="Name of the bucket to add")
@click.option(
    "--provider", default="s3", help="Cloud provider for the bucket (default: s3)"
)
@click.option(
    "--region", default="us-east-1", help="Region for the bucket (default: us-east-1)"
)
@click.option(
    "--endpoint", default="https://s3.amazonaws.com", help="Endpoint URL for the bucket"
)
@click.option("--auth-mode", default="iam", help="Authentication mode (default: iam)")
@click.pass_context
def update_command(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    name: str,
    provider: str,
    region: str,
    endpoint: str,
    auth_mode: str,
) -> None:
    """Update bucket."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    authz = to_resource_path(project_id)

    with CLIOutput(config=config) as output:
        try:
            auth = ensure_auth(config=config, validate=True)
            output.update({"endpoint": auth.endpoint})
            output.update(
                FenceAdminClient(auth).change_bucket(
                    name=name,
                    provider=provider,
                    region=region,
                    endpoint=endpoint,
                    auth_mode=auth_mode,
                    authz=[authz],
                )
            )
        except Exception as e:
            output.update({"msg": str(e)})
            if config.debug:
                raise e
            output.exit_code = 1


@bucket_group.command(name="ls")
@common_options
@click.pass_context
def ls_command(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
):
    """List buckets managed by commons."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        try:
            auth = ensure_auth(config=config, validate=True)
            output.update({"endpoint": auth.endpoint})
            output.update(FenceAdminClient(auth).list_buckets())
        except Exception as e:
            output.update({"msg": str(e)})
            if config.debug:
                raise e
            output.exit_code = 1


@bucket_group.command(name="rm")
@common_options
@click.option("--name", "name", type=str, nargs=1)
@click.pass_context
def rm_command(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    name: str,
    project_id: str,
):
    """Remove buckets from a project."""
    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    with CLIOutput(config=config) as output:
        try:
            auth = ensure_auth(config=config, validate=True)
            output.update({"endpoint": auth.endpoint})
            output.update(FenceAdminClient(auth).delete_bucket(name))
        except Exception as e:
            output.update({"msg": str(e)})
            if config.debug:
                raise e
            output.exit_code = 1
