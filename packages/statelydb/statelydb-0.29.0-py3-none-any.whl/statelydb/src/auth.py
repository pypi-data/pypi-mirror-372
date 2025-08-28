"""
Authentication code for the Stately Cloud SDK.

The authenticator function is a callable
that returns an access token string containing the auth token.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import random
from typing import TYPE_CHECKING, Any, Callable

from statelydb.lib.api.auth import get_auth_token_pb2
from statelydb.lib.api.auth import service_grpc as auth
from statelydb.src.channel import StatelyChannel
from statelydb.src.errors import StatelyError, Status

if TYPE_CHECKING:
    from statelydb.src.types import Stopper

# AuthTokenProvider is a callable that returns an auth token.
AuthTokenProvider = Callable[[], Coroutine[Any, Any, str]]

NON_RETRYABLE_ERRORS = [
    Status.UNAUTHENTICATED,
    Status.PERMISSION_DENIED,
    Status.NOT_FOUND,
    Status.UNIMPLEMENTED,
    Status.INVALID_ARGUMENT,
]
RETRY_ATTEMPTS = 10


@dataclass
class TokenResult:
    """Result from a token fetch operation."""

    token: str
    expires_in_secs: int


@dataclass
class TokenState:
    """Persistent state for the token provider."""

    token: str
    expires_at: datetime


# TokenFetcher is a callable that returns a TokenResult
# this is basically the abstraction that we swap out for different providers ie.
# auth0 or stately
TokenFetcher = Callable[[], Coroutine[Any, Any, TokenResult]]


def init_server_auth(  # noqa: C901
    access_key: str | None = None,
    base_retry_backoff_secs: float = 1.0,
) -> tuple[Callable[[str], AuthTokenProvider], Stopper]:
    """
    Create a new authenticator with the provided arguments.

    init_server_auth returns a tuple containing an func to start the token provder,
    and a Stopper function.

    :param access_key: Your Stately Access Key.
        Defaults to os.getenv("STATELY_ACCESS_KEY").
    :type access_key: str, optional

    :param base_retry_backoff_secs: The base backoff time in seconds for retrying failed requests.
        Defaults to 1.0.
    :type base_retry_backoff_secs: float, optional

    :return: A tuple containing a Callable[[str], AuthTokenProvider] and a stopper function.
    :rtype: tuple[Callable[[str], AuthTokenProvider], Stopper]

    """
    # args are evaluated at definition time
    # so we can't put these in the definition
    access_key = access_key or os.getenv("STATELY_ACCESS_KEY")

    token_fetcher: TokenFetcher | None = None
    token_fetcher_stopper: Stopper | None = None
    scheduled_refresh: asyncio.Task[Any] | None = None

    if access_key is None:
        raise StatelyError(
            stately_code="Unauthenticated",
            code=Status.UNAUTHENTICATED,
            message=(
                "Unable to find an access key in the STATELY_ACCESS_KEY environment variable."
                "Either pass your access key in the options when creating a client or set this environment variable."
            ),
        )

    # init nonlocal containing the initial state
    # this is overridden by the refresh function
    token_state: TokenState | None = None

    async def _refresh_token_impl() -> str:
        nonlocal token_state
        nonlocal scheduled_refresh
        scheduled_refresh = None

        token_result = await token_fetcher()  # type: ignore[misc] # mypy can't work out that this can't be None
        new_expires_in_secs = token_result.expires_in_secs
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=new_expires_in_secs
        )

        # only update the token state if the new expiry is later than the current one
        if token_state is None or new_expires_at > token_state.expires_at:
            token_state = TokenState(token_result.token, new_expires_at)
        else:
            # otherwise use the existing expiry time for scheduling the refresh.
            new_expires_in_secs = int(
                (token_state.expires_at - datetime.now(timezone.utc)).total_seconds()
            )

        # Calculate a random multiplier to apply to the expiry so that we refresh
        # in the background ahead of expiration, but avoid multiple processes
        # hammering the service at the same time.
        # This random generator is fine, it doesn't need to
        # be cryptographically secure.
        # ruff: noqa: S311
        jitter = (random() * 0.05) + 0.9

        # set the refresh task
        scheduled_refresh = asyncio.get_event_loop().create_task(
            _schedule(_refresh_token, new_expires_in_secs * jitter),
        )

        return token_state.token

    # _refresh_token will fetch the most current auth token for usage in Stately APIs.
    # This method is automatically invoked when calling get_token()
    # if there is no token available.
    # It is also periodically invoked to refresh the token before it expires.
    _refresh_token, _cancel_refresh = _dedupe(
        lambda: asyncio.create_task(_refresh_token_impl())
    )

    def valid_access_token() -> str | None:
        nonlocal token_state
        if (
            token_state is not None
            and datetime.now(
                timezone.utc,
            )
            < token_state.expires_at
        ):
            return token_state.token
        return None

    async def get_token() -> str:
        return valid_access_token() or await _refresh_token()

    def shutdown() -> None:
        nonlocal scheduled_refresh
        nonlocal token_fetcher_stopper
        _cancel_refresh()
        if scheduled_refresh is not None:
            scheduled_refresh.cancel()
            scheduled_refresh = None
        if token_fetcher_stopper is not None:
            token_fetcher_stopper()
            token_fetcher_stopper = None

    def start(endpoint: str = "https://api.stately.cloud") -> AuthTokenProvider:
        nonlocal token_fetcher, token_fetcher_stopper
        token_fetcher, token_fetcher_stopper = make_fetch_stately_access_token(
            access_key, endpoint, base_retry_backoff_secs
        )
        return get_token

    return start, shutdown


async def _schedule(fn: Callable[[], Awaitable[Any]], delay_secs: float) -> None:
    await asyncio.sleep(delay_secs)
    await fn()


# Dedupe multiple tasks
# If this this is called multiple times while the first task is running
# then the result of the first task will be returned to all callers
# and the other tasks will never be awaited
def _dedupe(
    create_task: Callable[..., asyncio.Task[Any]],
) -> tuple[Callable[..., Awaitable[Any]], Callable[..., None]]:
    cached_task: asyncio.Task[Any] | None = None

    async def _run() -> Awaitable[Any]:
        nonlocal cached_task
        cached_task = cached_task or create_task()
        try:
            return await cached_task
        finally:
            cached_task = None

    def _cancel() -> None:
        nonlocal cached_task
        if cached_task is not None:
            cached_task.cancel()
            cached_task = None

    return _run, _cancel


def make_fetch_stately_access_token(
    access_key: str, endpoint: str, base_retry_backoff_secs: float
) -> tuple[TokenFetcher, Stopper]:
    """make_fetch_stately_access_token creates a fetcher function that fetches a Stately token using access_key."""
    auth_service: auth.AuthServiceStub | None = None
    channel: StatelyChannel | None = None

    def stop() -> None:
        nonlocal channel
        if channel is not None:
            # you hit a runtime error if the event loop is already closed.
            # i think it is safe to ignore this.
            with contextlib.suppress(RuntimeError):
                channel.close()

    async def fetch_stately_access_token() -> TokenResult:
        nonlocal auth_service
        nonlocal channel
        # lazy init the auth service. It needs to be done in
        # an async context.
        if auth_service is None:
            channel = channel or StatelyChannel(endpoint=endpoint)
            auth_service = auth.AuthServiceStub(channel=channel)

        for i in range(RETRY_ATTEMPTS):
            try:
                resp = await auth_service.GetAuthToken(
                    get_auth_token_pb2.GetAuthTokenRequest(access_key=access_key)
                )
                return TokenResult(
                    token=resp.auth_token,
                    expires_in_secs=resp.expires_in_s,
                )
            except StatelyError as e:  # noqa: PERF203
                if e.code in NON_RETRYABLE_ERRORS or i == RETRY_ATTEMPTS - 1:
                    raise
                await asyncio.sleep(backoff(i, base_retry_backoff_secs))
                continue
        # You should never ever hit this. The loop should be raising the exception from the API
        # in the above error handler. If you do hit this, it means there is a programming error
        raise StatelyError(
            stately_code="Internal",
            code=Status.INTERNAL,
            message="Exceeded max retry attempts but did not correctly propagate exception on final attempt.",
        )

    return fetch_stately_access_token, stop


def backoff(attempt: int, base_retry_backoff_secs: float) -> float:
    """
    Calculate the duration to wait before retrying a request.

    :param attempt: The number of attempts that have been made so far.
    :type attempt: int

    :param base_retry_backoff_secs: The base backoff time in seconds.
    :type base_retry_backoff_secs: float

    :return: The duration to wait before retrying the request.
    :rtype: float

    """
    # Double the base backoff time per attempt, starting with 1
    exp = 2**attempt
    # Add a full jitter to the backoff time, from no wait to 100% of the exponential backoff.
    jitter = random()
    return exp * jitter * base_retry_backoff_secs
