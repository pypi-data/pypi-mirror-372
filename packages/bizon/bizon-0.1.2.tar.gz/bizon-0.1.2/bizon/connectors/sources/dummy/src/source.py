import random
from typing import List, Literal, Tuple, Union

from pydantic import Field
from requests.auth import AuthBase

from bizon.source.auth.authenticators.oauth import Oauth2AuthParams
from bizon.source.auth.authenticators.token import TokenAuthParams
from bizon.source.auth.builder import AuthBuilder
from bizon.source.auth.config import AuthConfig, AuthType
from bizon.source.config import SourceConfig, SourceSyncModes
from bizon.source.models import SourceIteration, SourceRecord
from bizon.source.source import AbstractSource

from .fake_api import fake_api_call

URL_TOKEN_REFRESH = "https://api.mydummysaas.com/oauth/v1/token"


class DummyAuthConfig(AuthConfig):
    type: Literal[AuthType.API_KEY, AuthType.OAUTH]
    params: Union[TokenAuthParams, Oauth2AuthParams] = Field(None, description="OAuth or API configuration")


class DummySourceConfig(SourceConfig):
    authentication: DummyAuthConfig
    sleep: int = Field(0, description="Sleep time in seconds between API calls")


class DummySource(AbstractSource):

    def __init__(self, config: DummySourceConfig):
        super().__init__(config)
        self.config = config

    @staticmethod
    def streams() -> List[str]:
        return ["creatures", "plants"]

    @staticmethod
    def get_config_class() -> SourceConfig:
        return DummySourceConfig

    @property
    def url_entity(self) -> str:
        return f"https://api.dummy.com/v1/{self.config.stream}"

    def get_authenticator(self) -> AuthBase:

        if self.config.authentication.type == AuthType.OAUTH:
            return AuthBuilder.oauth2(
                params=Oauth2AuthParams(
                    token_refresh_endpoint=URL_TOKEN_REFRESH,
                    client_id=self.config.authentication.params.client_id,
                )
            )

        if self.config.authentication.type == AuthType.API_KEY:
            return AuthBuilder.token(params=TokenAuthParams(token=self.config.authentication.params.token))

    def check_connection(self) -> Tuple[bool, str | None]:
        # Here we could check if the connection is established
        return True, None

    def get_total_records_count(self) -> int | None:
        # If available, return total number of records in the source for this stream
        # Otherwise, return None
        # In our case we have 5 records
        return 5

    def get(self, pagination: dict = None) -> SourceIteration:

        response: dict = None

        # If no pagination data is passed, we want to reach first page
        if not pagination:
            response = fake_api_call(url=self.url_entity, sleep=self.config.sleep)

        # If we have pagination data we pass it to the API
        else:
            response = fake_api_call(url=self.url_entity, cursor=pagination.get("cursor"), sleep=self.config.sleep)

        # Now we process the response to:
        # - allow bizon to process the records and write them to destination
        # - iterate on next page if needed

        # We parse records and next cursor from the response
        records = response.get("results")
        next_cursor = response.get("next", {}).get("cursor")

        next_pagination = {"cursor": next_cursor} if next_cursor else {}

        destination_id = None

        # If we are in streaming mode, we need to get the destination id from the stream name
        if self.config.sync_mode == SourceSyncModes.STREAM:
            if next_pagination.get("cursor") == "final-cursor":
                destination_id = "routed"
            else:
                destination_id = self.config.stream

        if records:
            return SourceIteration(
                next_pagination=next_pagination,
                records=[
                    SourceRecord(
                        id=record["id"],
                        data=record,
                        destination_id=destination_id,
                    )
                    for record in records
                ],
            )

        return SourceIteration(
            next_pagination=next_pagination,
            records=[],
        )
