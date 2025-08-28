"""Helpers for working with Stately Item keys."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from uuid import UUID

from grpclib.const import Status

from statelydb.src.errors import StatelyError

if TYPE_CHECKING:
    from statelydb.src.types import AllKeyTypes


def key_path(template: str, **kwargs: AllKeyTypes) -> str:
    """
    Construct a key path a template and a dict of named values.

    :return: The fully formed key path
    :rtype: str

    :raises StatelyError: If a provided value is not a supported type

    Examples
    --------
    .. code-block:: python
        key = key_path("/foo-{id}", id="bar")
        print(key) # "/foo-bar"
        key = key_path("/foo-{id1}/baz-{id2}", id1="bar", id2="qux")
        print(key) # "/foo-bar/baz-qux"

    """
    processed_kwargs = {key: key_id(value) for key, value in kwargs.items()}
    return template.format(**processed_kwargs)


def key_id(val: AllKeyTypes) -> str:
    """
    Generate a key ID from a value of a supported type.
    This will encode the value into the correct Stately format.

    :param val: The key ID value to encode
    :type val: AllKeyTypes

    :return: The encoded key ID
    :rtype: str

    :raises StatelyError: If the value is not a supported type,
        or if the value is invalid
    """
    if isinstance(val, bytes):
        return f"{encode_bytes(val)}"
    if isinstance(val, str):
        return val.replace("/", "%/")
    if isinstance(val, int):
        return str(val)
    if isinstance(val, UUID):  # type: ignore[reportUnnecessaryIsInstance]
        return str(val)
    raise StatelyError(
        stately_code="InvalidKeyPath",
        code=Status.INVALID_ARGUMENT,
        message=f"Unsupported key ID type: {type(val)}",
    )


def encode_bytes(val: bytes) -> str:
    """
    Encode bytes into a base64 string that is safe for use in a key ID.

    :param val: The bytes to encode
    :type val: bytes

    :return: The encoded base64 string
    :rtype: str
    """
    return base64.b64encode(val, altchars=b"-_").decode("ascii").replace("=", "")
