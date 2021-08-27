import logging

import google.auth
import google.auth.transport.requests
import requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)


class GoogleInterface:
    def __init__(self):

        self.request = google.auth.transport.requests.Request()
        # todo add audience
        self.target_audience = ""

    def current_service_account_email(self):
        try:
            # ON CLOUD RUN WE NEED TO TALK WITH THE METASERVER
            url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts"
            response = requests.get(url, headers={"Metadata-Flavor": "Google"})
            return response.content.decode("utf-8")
        except requests.exceptions.ConnectionError:
            credentials, _ = google.auth.default()
            return credentials.service_account_email

    def generate_id_token(self, audience=None) -> str:

        # Generate an id_token with de current ENV SERVICE ACCOUNT

        aud = audience if audience is not None else self.target_audience

        open_id_connect_token = id_token.fetch_id_token(self.request, aud)

        return open_id_connect_token

    def verify_id_token(self, id_token_to_verify: str) -> bool:

        # Check if the id_token match with de current ENV SERVICE ACCOUNT EMAIL
        # AND with the good AUDIENCE

        try:
            result = id_token.verify_token(id_token_to_verify, self.request)

            if (
                result
                and result["aud"] == self.target_audience
                and result["email"] in self.current_service_account_email()
            ):

                return True

            else:

                return False

        except Exception as err:

            logger.error(err)

            return False
