from gen3.auth import Gen3Auth

from calypr_admin.config import Config, ensure_auth
from calypr_admin.admin.projects import ProjectSummaries, get_projects, ProjectSummary


def ls(
    config: Config,
    resource_filter: str | None = None,
    msgs: list[str] | None = None,
    auth: Gen3Auth | None = None,
) -> ProjectSummaries:
    """List projects."""

    if not msgs:
        msgs = []
    if not auth:
        auth = ensure_auth(config=config)

    if not auth:
        raise ValueError("auth required")

    projects = get_projects(auth)

    # if full:
    project_messages = {}
    for _program in projects:
        for _project in projects[_program]:
            if (
                resource_filter
                and resource_filter != f"/programs/{_program}/projects/{_project}"
            ):
                continue
            project_messages[f"/programs/{_program}/projects/{_project}"] = (
                ProjectSummary(
                    permissions=projects[_program][_project]["permissions"],
                ).model_dump()
            )

    if len(project_messages) == 0:
        msgs.append("No projects found.")

    return ProjectSummaries(
        **{"endpoint": auth.endpoint, "projects": project_messages, "messages": msgs}
    )
