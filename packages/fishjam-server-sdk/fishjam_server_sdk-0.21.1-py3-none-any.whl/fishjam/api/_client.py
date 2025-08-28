from typing import cast

from fishjam._openapi_client.client import AuthenticatedClient
from fishjam._openapi_client.models import Error
from fishjam._openapi_client.types import Response
from fishjam.errors import HTTPError
from fishjam.utils import get_fishjam_url


class Client:
    def __init__(
        self, fishjam_id: str, management_token: str, *, fishjam_url: str | None = None
    ):
        self._fishjam_url = get_fishjam_url(fishjam_id, fishjam_url)
        self.client = AuthenticatedClient(self._fishjam_url, token=management_token)

    def _request(self, method, **kwargs):
        response = method.sync_detailed(client=self.client, **kwargs)

        if isinstance(response.parsed, Error):
            response = cast(Response[Error], response)
            raise HTTPError.from_response(response)

        return response.parsed
