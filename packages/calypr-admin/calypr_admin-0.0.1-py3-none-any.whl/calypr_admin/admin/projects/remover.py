import asyncio
import sys

import click
from gen3.jobs import Gen3Jobs
from gen3.submission import Gen3Submission

from calypr_admin.config import Config, ensure_auth


def empty(config: Config, project_id: str, wait: bool = True) -> dict:
    """Empty all meta data (graph, flat) for a project. Delete project."""

    assert "-" in project_id, f"Invalid project_id: {project_id}"
    program, project = project_id.split("-")
    assert program and project, f"Invalid project_id: {project_id}"

    auth = ensure_auth(config=config)
    jobs_client = Gen3Jobs(auth_provider=auth)
    args = {"object_id": None, "project_id": project_id, "method": "delete"}

    if wait:
        _ = asyncio.run(jobs_client.async_run_job_and_wait("fhir_import_export", args))
        try:
            submission = Gen3Submission(auth_provider=auth)
            r = submission.delete_project(program, project)
            r.raise_for_status()
        except Exception as e:
            click.secho(f"Error deleting project data: {e}", fg="red", file=sys.stderr)
    else:
        _ = jobs_client.create_job("fhir_import_export", args)
        _ = {"output": _}
    return _
