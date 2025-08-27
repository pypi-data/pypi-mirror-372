import requests
from cmsdials.auth.bearer import Credentials
from cmsdials.utils.api_client import BaseAPIClient
from cmsdials.utils.logger import logger
from requests.exceptions import HTTPError


class DialsMinioClient(BaseAPIClient):
    default_timeout = 30
    lookup_url = "minio/"

    def __init__(
        self,
        creds: Credentials,
        *args: str,
        **kwargs: str,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.creds = creds

    def _build_headers(self) -> dict:
        base = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self._build_user_agent(),
        }
        self.creds.before_request(base)
        return base

    def presigned_put_object(self, workspace: str, object_name: str) -> str:
        headers = self._build_headers()
        endpoint_url = self.api_url + self.lookup_url + "ml-presigned-put-object/"
        response = requests.post(
            endpoint_url,
            headers=headers,
            json={"workspace": workspace, "object_name": object_name},
            timeout=self.default_timeout,
        )

        try:
            response.raise_for_status()
        except HTTPError as err:
            logger.debug("Api response text: %s", response.text)
            raise err

        return response.json()["url"]
