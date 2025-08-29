import os
from typing import Any
from typing import Dict
from urllib.parse import urlencode
from urllib.parse import urljoin

import quartzbio

from httpx_oauth.oauth2 import BaseOAuth2


class QuartzBioOAuth2(BaseOAuth2[Dict[str, Any]]):
    """Class implementing OAuth2 for QuartzBio API"""

    # QuartzBio API OAuth2 endpoints
    QUARTZBIO_URL = os.environ.get("QUARTZBIO_URL")
    OAUTH2_TOKEN_URL = "/v1/oauth2/token"
    OAUTH2_REVOKE_TOKEN_URL = "/v1/oauth2/revoke_token"

    def __init__(self, client_id, client_secret, name="quartzbio"):
        if not self.QUARTZBIO_URL:
            raise ValueError("QUARTZBIO_URL environment variable not set")

        super().__init__(
            client_id,
            client_secret,
            self.QUARTZBIO_URL,
            urljoin(quartzbio.get_api_host(), self.OAUTH2_TOKEN_URL),
            revoke_token_endpoint=urljoin(
                quartzbio.get_api_host(), self.OAUTH2_REVOKE_TOKEN_URL
            ),
            name=name,
        )

    def get_authorization_url(self, redirect_uri):
        """Creates authorization url for OAuth2"""

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
        }

        return "{}/authorize?{}".format(self.authorize_endpoint, urlencode(params))
