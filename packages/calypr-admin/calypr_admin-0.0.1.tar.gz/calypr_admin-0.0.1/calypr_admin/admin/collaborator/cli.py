import sys
from typing import Any

import click
from halo import Halo

from calypr_admin import NaturalOrderGroup
from calypr_admin.admin.collaborator.access.requestor import update
from calypr_admin.common import CLIOutput, ERROR_COLOR, validate_email, common_options
from calypr_admin.config import Config, ensure_auth, ensure_config


@click.group(name="collaborators", cls=NaturalOrderGroup)
@click.pass_context
def collaborator_group(ctx):
    """Manage project membership."""
    pass


@collaborator_group.command(name="add")
@click.argument("username", required=True, type=str)
@click.argument("resource_path", required=False, type=str)
@click.option(
    "--write/--no-write",
    "-w",
    help="Give user write privileges",
    is_flag=True,
    default=False,
    show_default=True,
)
# @click.option('--delete/--no-delete', '-d', help='Give user delete privileges', is_flag=True, default=False, show_default=True)
@click.option(
    "--approve",
    "-a",
    help="Approve the addition (privileged)",
    is_flag=True,
    default=False,
    show_default=True,
)
@common_options
@click.pass_context
def project_add_user(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    username: str,
    resource_path: str,
    write: bool,
    approve: bool,
):
    """Add user to project."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    import calypr_admin.admin.collaborator.access.requestor
    from calypr_admin.admin.collaborator.access.requestor import add_user, update

    assert username, "username (email) required"
    if resource_path:
        resource_path = resource_path.split("/")
        program = resource_path[2]
        project = resource_path[4]
        project_id = f"{program}-{project}"
    else:
        if not project_id:
            project_id = config.gen3.project_id
        program, project = project_id.split("-")

    if not program:
        raise ValueError("program required")

    if not project:
        raise ValueError("project required")

    with CLIOutput(config=config) as output:
        try:
            with Halo(
                text="Searching", spinner="line", placement="right", color="white"
            ):
                auth = ensure_auth(config=config)
                existing_requests = calypr_admin.admin.collaborator.access.requestor.ls(
                    config=config, mine=False, auth=auth, username=username
                ).requests
                existing_requests = [
                    r
                    for r in existing_requests
                    if r["resource_display_name"] == project_id
                ]
                needs_approval = []

                _ = add_user(
                    config,
                    project_id,
                    username,
                    write,
                    delete=False,
                    auth=auth,
                    existing_requests=existing_requests,
                )
                existing_requests = _.requests

                for request in existing_requests:
                    if request["status"] != "SIGNED":
                        needs_approval.append(request)

            if approve and not needs_approval:
                click.secho(
                    f"User {username} already has approved requests for {project_id}.",
                    fg="yellow",
                )
                output.update(
                    {
                        "existing": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in existing_requests
                        ]
                    }
                )

            elif not approve and needs_approval:
                output.update(
                    {
                        "needs_approval": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in needs_approval
                        ],
                        "msg": f"An authorized user must approve these requests to add {username} to {project_id} see --approve",
                    }
                )
            else:
                approvals = []
                with Halo(
                    text="Approving", spinner="line", placement="right", color="white"
                ):
                    for request in needs_approval:
                        approvals.append(
                            update(
                                config,
                                request_id=request["request_id"],
                                status="SIGNED",
                                auth=auth,
                            ).request
                        )
                output.update(
                    {
                        "approved": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in approvals
                        ]
                    }
                )

        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


@collaborator_group.command(name="rm")
@click.argument("username", required=True, type=str)
@click.option(
    "--approve",
    "-a",
    help="Approve the removal (privileged)",
    is_flag=True,
    default=False,
    show_default=True,
)
@common_options
@click.pass_context
def project_rm_user(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    username: str,
    approve: bool,
):
    """Remove user from project."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    from calypr_admin.admin.collaborator.access.requestor import rm_user, update

    with CLIOutput(config=config) as output:
        try:
            assert username, "username (email) required"
            assert project_id, "project_id required"

            approvals = []
            needs_approval = []
            auth = ensure_auth(config=config)
            with Halo(
                text="Removing", spinner="line", placement="right", color="white"
            ):
                _ = rm_user(config, project_id, username)
                needs_approval.extend(_.requests)
            if approve:
                with Halo(
                    text="Approving", spinner="line", placement="right", color="white"
                ):
                    for request in needs_approval:
                        _ = update(
                            config,
                            request_id=request["request_id"],
                            status="SIGNED",
                            auth=auth,
                        ).request
                        approvals.append(_)
                output.update(
                    {
                        "approved": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                            }
                            for r in approvals
                        ]
                    }
                )
            else:
                output.update(
                    {
                        "needs_approval": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                            }
                            for r in needs_approval
                        ]
                    }
                )

        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


@collaborator_group.command(name="ls")
@common_options
@click.pass_context
def project_ls_user(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
):
    """List all requests in project."""
    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    import calypr_admin.admin.collaborator.access.requestor

    with CLIOutput(config=config) as output:
        try:
            program = config.gen3.program
            project = config.gen3.project
            project_id = f"{program}-{project}"

            with Halo(
                text="Searching", spinner="line", placement="right", color="white"
            ):
                auth = ensure_auth(config=config)
                # get all requests
                existing_requests = calypr_admin.admin.collaborator.access.requestor.ls(
                    config=config, mine=False, auth=auth
                ).requests
                # filter for project
                existing_requests_for_project = [
                    r
                    for r in existing_requests
                    if r.get("resource_display_name", None) == project_id
                ]
                output.update(
                    {
                        "existing": [
                            {
                                "policy_id": r["policy_id"],
                                "resource_display_name": r["resource_display_name"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                                "updated_time": r["updated_time"],
                            }
                            for r in existing_requests_for_project
                        ]
                    }
                )

        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e


@collaborator_group.command(name="pending")
@common_options
@click.pass_context
def project_ls_pending(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
):
    """Show all pending requests."""

    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    import calypr_admin.admin.collaborator.access.requestor

    with CLIOutput(config=config) as output:
        try:
            with Halo(
                text="Searching", spinner="line", placement="right", color="white"
            ):
                auth = ensure_auth(config=config)
                existing_requests = calypr_admin.admin.collaborator.access.requestor.ls(
                    config=config, mine=False, auth=auth
                ).requests
                needs_approval = []
                for request in existing_requests:
                    if request["status"] != "SIGNED":
                        needs_approval.append(request)

                output.update(
                    {
                        "existing": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in needs_approval
                        ]
                    }
                )

        except Exception as e:
            click.secho(str(e), fg=ERROR_COLOR, file=sys.stderr)
            output.exit_code = 1
            if config.debug:
                raise e


@collaborator_group.command(name="approve")
@click.option("--request_id", required=False, help="Sign only this request")
@click.option(
    "--all", "all_requests", required=False, is_flag=True, help="Sign all requests"
)
@common_options
@click.pass_context
def project_approve_request(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    request_id: str,
    all_requests: bool,
):
    """Sign an existing request (privileged)."""
    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    import calypr_admin.admin.collaborator.access.requestor
    from calypr_admin.admin.collaborator.access.requestor import update

    with CLIOutput(config=config) as output:
        try:
            assert request_id or all_requests, "request_id or --all required"
            with Halo(text="Signing", spinner="line", placement="right", color="white"):
                auth = ensure_auth(config=config)
                program = config.gen3.program
                project = config.gen3.project
                if all_requests:
                    existing_requests: list[dict[Any, Any]] = (
                        calypr_admin.admin.collaborator.access.requestor.ls(
                            config=config, mine=False, auth=auth
                        ).requests
                    )

                    if program and project:
                        existing_requests: list[dict[Any, Any]] = [
                            r
                            for r in existing_requests
                            if r["resource_display_name"] == f"{program}-{project}"
                        ]
                    needs_approval = []
                    for request in existing_requests:
                        if "status" not in request:
                            raise ValueError(f"status not in {request}")
                        if request["status"] != "SIGNED":
                            needs_approval.append(request)

                    approved: list[dict[str, Any]] = []
                    assert (
                        len(needs_approval) > 0
                    ), "No requests to approve.  You must be a privileged user to approve requests."
                    for request in needs_approval:
                        approved.append(
                            update(
                                config,
                                request_id=request["request_id"],
                                status="SIGNED",
                                auth=auth,
                            ).request
                        )
                    output.update(
                        {
                            "approved": [
                                {
                                    "policy_id": r["policy_id"],
                                    "request_id": r["request_id"],
                                    "status": r["status"],
                                    "username": r["username"],
                                }
                                for r in approved
                            ]
                        }
                    )
                else:
                    r: dict[str, Any] = update(
                        config, request_id=request_id, status="SIGNED", auth=auth
                    ).request
                    output.update(
                        {
                            "approved": [
                                {
                                    "policy_id": r["policy_id"],
                                    "request_id": r["request_id"],
                                    "status": r["status"],
                                    "username": r["username"],
                                }
                            ]
                        }
                    )

        except Exception as e:
            click.secho(str(e), fg=ERROR_COLOR, file=sys.stderr)
            output.exit_code = 1
            if config.debug:
                raise e


@collaborator_group.command(name="add-steward", hidden=True)
@click.argument("user_name", required=True)
@click.argument("resource_path", required=True)
@click.option(
    "--approve",
    "-a",
    help="Approve the addition (privileged)",
    is_flag=True,
    default=False,
    show_default=True,
)
@common_options
@click.pass_context
def add_steward(
    ctx: click.Context,
    output_format: str,
    profile: str,
    debug: bool,
    dry_run: bool,
    project_id: str,
    resource_path: str,
    user_name: str,
    approve: bool,
):
    """Add a data steward user with approval rights to a program.

    \b
    USER_NAME (str): user's email
    RESOURCE_PATH (str): Gen3 authz /programs/<program>
    """
    ensure_config(ctx, output_format, profile, debug, dry_run)
    config: Config = ctx.obj

    from calypr_admin.admin.collaborator.access import create_request

    with CLIOutput(config=config) as output:
        try:

            msgs = validate_email(user_name)
            assert msgs == [], f"Invalid email address: {user_name} {msgs}"
            assert user_name, "user_name required"

            request = {"username": user_name, "resource_path": resource_path}
            roles = ["requestor_reader_role", "requestor_updater_role"]

            needs_approval = []
            approvals: list[dict[str, Any]] = []
            with Halo(text="Adding", spinner="line", placement="right", color="white"):
                auth = ensure_auth(config=config)

                user = auth.curl("/user/user").json()
                is_privileged = False
                for _ in user["authz"]["/programs"]:
                    if _["method"] == "update" and _["service"] == "requestor":
                        is_privileged = True
                        break
                assert is_privileged, "You must be a privileged user to add a steward."

                for role in roles:
                    request.update({"role_ids": [role]})
                    needs_approval.append(
                        create_request(config=config, request=request)
                    )

            if approve:
                with Halo(
                    text="Approving", spinner="line", placement="right", color="white"
                ):
                    for request in needs_approval:
                        approvals.append(
                            update(
                                config,
                                request_id=request["request_id"],
                                status="SIGNED",
                                auth=auth,
                            ).request
                        )
                output.update(
                    {
                        "approved": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in approvals  # r: dict[str, Any]
                        ]
                    }
                )
            else:
                output.update(
                    {
                        "needs_approval": [
                            {
                                "policy_id": r["policy_id"],
                                "request_id": r["request_id"],
                                "status": r["status"],
                                "username": r["username"],
                            }
                            for r in needs_approval
                        ]
                    }
                )

        except Exception as e:
            output.update({"msg": str(e)})
            output.exit_code = 1
            if config.debug:
                raise e
