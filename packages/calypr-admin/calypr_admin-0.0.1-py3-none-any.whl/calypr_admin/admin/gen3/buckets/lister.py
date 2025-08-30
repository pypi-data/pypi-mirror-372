from pydantic import BaseModel

from calypr_admin.admin.gen3.buckets import get_buckets
from calypr_admin.config import Config, ensure_auth


class LogBuckets(BaseModel):
    endpoint: str
    """The commons url"""
    buckets: dict
    """List of buckets"""


# add a cache to this to avoid hitting arborist too much (or at all), time it out after 1 hour


def ls(config: Config):
    """List projects."""
    auth = ensure_auth(config=config)
    buckets = get_buckets(auth=auth)
    return LogBuckets(**{"endpoint": auth.endpoint, "buckets": buckets})
