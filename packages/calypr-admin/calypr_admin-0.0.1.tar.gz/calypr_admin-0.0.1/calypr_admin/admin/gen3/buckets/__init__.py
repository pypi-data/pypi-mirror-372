import json
import logging

from gen3.auth import Gen3Auth


def get_buckets(auth: Gen3Auth = None) -> dict:
    """LEGACY Fetch information about the buckets."""
    # LEGACY
    response = auth.curl("/user/data/buckets")

    # TODO - remove when no longer needed
    if response.status_code == 405:
        logging.getLogger(__name__).warning(
            "TODO /data/buckets response returned 405, "
            "see https://cdis.slack.com/archives/CDDPLU1NU/p1683566639636949 "
            "see quay.io/cdis/fence:feature_bucket_info_endpoint "
        )

    assert response.status_code == 200, (response.status_code, response.content)
    return response.json()


# def get_program_bucket(
#     program: str, auth: Gen3Auth = None
# ) -> str:
#     """LEGACY Get the bucket for a program."""
#     buckets = get_buckets(auth=auth)
#     bucket_name = None
#
#     for k, v in buckets["S3_BUCKETS"].items():
#         assert "programs" in v, f"no configured programs in fence buckets {v} {buckets}"
#         if program in v["programs"]:
#             bucket_name = k
#             break
#     # assert bucket_name, f"could not find bucket for {program}"
#     return bucket_name


class FenceAdminClient:
    def __init__(self, auth: Gen3Auth) -> None:
        """
        Initialize the FenceAdminClient.

        Args:
            auth (Gen3Auth): Authenticated Gen3Auth instance.
        """
        self.auth = auth

    def list_buckets(self) -> dict:
        """
        List all buckets.

        Returns:
            dict: List of bucket information.
        """
        resp = self.auth.curl("/admin/buckets")
        resp.raise_for_status()
        return resp.json()

    def add_bucket(
        self,
        name: str,
        provider: str,
        region: str,
        endpoint: str,
        auth_mode: str,
        authz: list,
    ) -> dict:
        """
        Add a new bucket.

        Args:
            name (str): Name of the bucket.
            provider (str): Provider of the bucket (e.g., aws, gcp).
            region (str): Region of the bucket.
            endpoint (str): Endpoint URL for the bucket.
            auth_mode (str): Authentication mode (e.g., iam, access_key).
            authz (list): List of authorization paths

        Returns:
            dict: Response from the server.
        """
        bucket_data = {
            "name": name,
            "provider": provider,
            "region": region,
            "endpoint": endpoint,
            "auth_mode": auth_mode,
            "authz": authz,
        }
        resp = self.auth.curl("/admin/buckets", "POST", data=json.dumps(bucket_data))
        resp.raise_for_status()
        return resp.json()

    def change_bucket(
        self,
        name: str,
        provider: str,
        region: str,
        endpoint: str,
        auth_mode: str,
        authz: list,
    ) -> dict:
        """
        Update an existing bucket.

        Args:
            name (str): Name of the bucket to update.
            update_data (dict): Data to update.

        Returns:
            dict: Response from the server.
        """
        update_data = {
            "name": name,
            "provider": provider,
            "region": region,
            "endpoint": endpoint,
            "auth_mode": auth_mode,
            "authz": authz,
        }

        resp = self.auth.curl(
            f"admin/buckets/{name}", request="PUT", data=json.dumps(update_data)
        )
        resp.raise_for_status()
        return resp.json()

    def delete_bucket(self, name: str) -> dict:
        """
        Delete a bucket.
        Args:
            name (str): Name of the bucket to delete.
        Returns:
            dict: Response from the server.
        """
        resp = self.auth.curl(f"admin/buckets/{name}", request="DELETE")
        resp.raise_for_status()
        return resp.json()
