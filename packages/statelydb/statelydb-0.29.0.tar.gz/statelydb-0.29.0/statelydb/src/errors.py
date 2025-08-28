"""Code for handling errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from grpclib.const import Status

from statelydb.lib.api.errors import error_details_pb2 as pb_error

if TYPE_CHECKING:
    from grpclib.events import RecvTrailingMetadata


class StatelyError(Exception):
    """
    StatelyError is an exception that is raised by Stately when an error
    occurs while talking to the Stately API or within the SDK.

    Where possible these errors will contain a `stately_code` which can be
    searched for in the Stately API documentation to find out more about the
    error.

    For API errors, the `grpc_code` will contain the gRPC status code that was
    returned by the Stately API. This may be useful for debugging or writing
    code that handles specific errors.
    """

    def __init__(
        self,
        stately_code: str,
        code: Status | int,
        message: str | None = None,
        cause: str | Exception | None = None,
    ) -> None:
        """
        Create a new StatelyError.

        :param stately_code: The Stately error code. This is either parsed from the gRPC
            response or supplied by the SDK for errors that occur within the SDK.
        :type stately_code: str
        :param code: The ConnectRPC/gRPC status code that was returned by the Stately
            API.
        :type code: Status | int
        :param message: A human readable message that describes the error.
        :type message: str | None
        :param cause: An optional param containing the cause of the error.
            This can be a string or an exception thrown directly by the SDK.
        :type cause: str | Exception | None
        """
        super().__init__(message)

        self.stately_code = stately_code
        if isinstance(code, int):
            try:
                self.code = Status(code)
            except ValueError:
                self.code = Status.UNKNOWN
        else:
            self.code = code
        self.message = message
        self.cause = cause

    def __repr__(self) -> str:
        """Print a human readable represenation of the error."""
        # put it in camel case
        grpc_code_name = "".join(
            x.capitalize() for x in self.code.name.lower().split("_")
        )
        code_string = f"{grpc_code_name}/{self.stately_code}"
        return (
            f"({code_string}) {self.message}"
            if (self.message and len(self.message))
            else f"({code_string})"
        )

    __str__ = __repr__

    @staticmethod
    def from_trailing_metadata(event: RecvTrailingMetadata) -> StatelyError:
        """
        Parse a StatelyError from grpc trailing metadata.

        :param event: The event to parse
        :type event: RecvTrailingMetadata
        :return: The parsed error.
        :rtype: StatelyError
        """
        if (
            isinstance(event.status_details, list)
            and len(event.status_details)  # type: ignore[reportUnknownMemberType]
            and isinstance(
                event.status_details[0],  # type: ignore[reportUnknownMemberType]
                pb_error.StatelyErrorDetails,
            )
        ):
            detail = event.status_details[0]  # type: ignore[reportUnknownMemberType]
            message = detail.message
            return StatelyError(
                stately_code=detail.stately_code,
                message=message,
                code=event.status,
                cause=detail.upstream_cause,
            )
        return StatelyError(
            stately_code="Unknown",
            message=event.status_message,
            code=event.status,
            cause=None,
        )
