from typing import Optional

from cmsdials.auth.bearer import Credentials
from cmsdials.auth.client import AuthClient

from ..config import Config


def get_credentials(base_url: Optional[str]) -> Credentials:
    auth = AuthClient(base_url=base_url)
    cache_dir = None if base_url is None else Config.dials_dev_cache_dir
    return Credentials.from_creds_file(cache_dir=cache_dir, client=auth)
