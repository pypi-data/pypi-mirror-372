from typing import List

import calypr_admin
from calypr_admin.admin.collaborator.access.requestor import add_policies
from calypr_admin.admin.projects.lister import ls as project_ls
from calypr_admin.config import ensure_auth


def initialize_project_server_side(
    config, project_id, force=False, auth=None
) -> (List[str], bool):
    """Initialize a project in the current directory."""
    if not project_id:
        raise ValueError("project_id required")

    if auth is None:
        if not config.gen3.profile:
            raise ValueError("profile required")
        auth = ensure_auth(config=config)

    logs = []
    program, project = project_id.split("-")

    existing_requests = calypr_admin.admin.collaborator.access.requestor.ls(
        config=config, mine=False, auth=auth
    ).requests
    existing_requests = [
        _
        for _ in existing_requests
        if program in _.get("policy_id", "") and project in _.get("policy_id", "")
    ]
    if len(existing_requests) > 0:
        usernames = [_.get("username", "unknown") for _ in existing_requests]
        request_ids = [_.get("request_id", "unknown") for _ in existing_requests]
        msg = f"Project creation requests already exist for users {list(set(usernames))}. request_ids {request_ids}"
        if force:
            logs.append(msg)
        else:
            raise ValueError(msg)

    summaries = project_ls(config, auth=auth)
    existing_project = [_ for _ in summaries.projects if _.endswith(project)]
    policy_msgs = []
    # looking for project to exist, but not reader permissions on project, then sign project.
    # If at least reader permissions then carry on.
    if len(existing_project) > 0:
        logs.append(
            f"Pending request for project creation. Admin must sign access request for: /{program}/projects/{project}"
        )
        return logs, False
    else:
        _ = add_policies(config, project_id, auth=auth)
        policy_msgs.extend([_.msg, f"See {_.commands}"])
        logs.extend(policy_msgs)
    return logs, True
