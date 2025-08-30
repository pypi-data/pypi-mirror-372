import sys
import os
import logging
from synmax.openapi.client import OpenAPIClient



current_dir = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(f'%(levelname)s {__name__} - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class HyperionApiClient(OpenAPIClient):
    _spec = os.path.join(current_dir, "openapi.yaml")

    def __init__(self, access_token: str,
                 base_uri: str = "https://hyperion.api.synmax.com/v4/",
                 timeout = 30.0,
                 retries = 3,
                 retry_sleep = 30,
                 ):
        super().__init__(
            base_uri,
            headers={"Access-Key": access_token},
            logger=logger,
            timeout=timeout,
            retry_sleep=retry_sleep
        )
