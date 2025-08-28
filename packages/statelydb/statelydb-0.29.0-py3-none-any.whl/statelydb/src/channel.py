"""Custom gRPC channel for StatelyDB."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from grpclib.client import Channel
from grpclib.const import Status
from grpclib.encoding.proto import ProtoStatusDetailsCodec
from grpclib.events import RecvTrailingMetadata, SendRequest, listen

from statelydb.src.errors import StatelyError

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from statelydb.src.auth import AuthTokenProvider


class StatelyChannel(Channel):
    """
    Custom gRPC channel for StatelyDB.
    This channel automatically resolves the correct endpoint for the region
    and wraps all requests in StatelyError conversion middleware.
    """

    _endpoint: str

    def __init__(
        self,
        *,
        endpoint: str,
    ) -> None:
        """
        Create a new StatelyChannel.

        :param endpoint: The Stately API endpoint to connect to.
        :type endpoint: str

        :param region: The Stately region to connect to.
            If region is provided and endpoint is not provided then the regional
            endpoint will be used.
        :type region: str, optional
        """
        self._endpoint = endpoint
        url = urlparse(endpoint)
        super().__init__(  # type: ignore[reportUnknownMemberType]
            host=url.hostname,
            port=url.port or (443 if url.scheme == "https" else 80),
            ssl=url.scheme == "https",
            status_details_codec=ProtoStatusDetailsCodec(),
        )
        # this is a hook that is called after a response is received
        # and parses StatelyErrors from the trailing metadata
        listen(self, RecvTrailingMetadata, _recv_trailing_metadata)

    def with_auth(self, *, token_provider: AuthTokenProvider) -> StatelyChannel:
        """
        Returns a clone of the channel which has authentication enabled.
        The Authorization header will be added to all outgoing requests using the provided token provider.

        :param token_provider: A function that returns an access token string.
        :type token_provider: AuthTokenProvider

        :return: A new StatelyChannel with the provided token provider.
        :rtype: StatelyChannel
        """
        new_channel = StatelyChannel(endpoint=self._endpoint)
        listen(new_channel, SendRequest, _make_send_request_handler(token_provider))
        return new_channel


async def _recv_trailing_metadata(event: RecvTrailingMetadata) -> None:
    """Hook that is called after a response is received."""
    if event.status != Status.OK:
        # from None stops the
        # "During handling of the above exception, another exception occurred"
        # which happens when raising an exception from a transaction handler.
        raise StatelyError.from_trailing_metadata(event) from None


def _make_send_request_handler(
    token_provider: AuthTokenProvider,
) -> Callable[[SendRequest], Coroutine[None, None, None]]:
    async def send_request(event: SendRequest) -> None:
        event.metadata["authorization"] = f"Bearer {await token_provider()}"

    return send_request
