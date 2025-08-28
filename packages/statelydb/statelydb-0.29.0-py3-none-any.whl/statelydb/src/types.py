"""Shared types for the Stately Cloud SDK."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, TypeVar, Union
from uuid import UUID

from statelydb.src.errors import StatelyError

if TYPE_CHECKING:
    from google.protobuf.message import Message

    from statelydb.lib.api.db.item_pb2 import Item as PBItem

StoreID = int
SchemaVersionID = int
SchemaID = int

AllKeyTypes = Union[UUID, str, int, bytes]
AnyKeyType = TypeVar("AnyKeyType", bound=AllKeyTypes)

Stopper = Callable[[], None]


class StatelyObject(ABC):
    """All generated object types must implement the StatelyObject interface."""

    @abstractmethod
    def marshal(self) -> Message:
        """Marshal the StatelyObject to its corresponding proto message."""

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes | Message) -> StatelyObject:
        """Unmarshal proto bytes or message into their corresponding StatelyObject."""


class StatelyItem(ABC):
    """All generated item types must implement the StatelyItem interface."""

    # this is set during unmarshalling to ensure that the key path
    # is not changed during the lifetime of the object.
    # You can see the check below in the marshal method.
    _primary_key_path: str | None = None

    def __init__(self) -> None:
        """
        Constructor for StatelyItem. This runs any setup that is common to
        all StatelyItems.
        """
        self._primary_key_path = None

    @abstractmethod
    def key_path(self) -> str:
        """Returns the Key Path of the current Item."""

    @abstractmethod
    def marshal(self) -> PBItem:
        """Marshal the StatelyItem to a protobuf Item."""

    def check_item_key_reuse(self) -> None:
        """Verify that the Key Path of the Item has not changed since it was read from StatelyDB."""
        if (
            self._primary_key_path is not None
            and self._primary_key_path != self.key_path()
        ):
            msg = (
                f'{self.item_type()} was read with Key Path: "{self._primary_key_path}" '
                f'but is being written with Key Path: "{self.key_path()}". '
                f"If you intend to move your {self.item_type()}, you should delete the "
                f"original and create a new one. If you intend to create a new {self.item_type()} "
                f"with the same data, you should create a new instance of {self.item_type()} "
                "rather than reusing the read result."
            )
            raise StatelyError(
                stately_code="ItemReusedWithDifferentKeyPath",
                code=3,  # InvalidArgument
                message=msg,
            )

    @staticmethod
    @abstractmethod
    def unmarshal(proto_bytes: bytes) -> StatelyItem:
        """Unmarshal proto bytes into their corresponding StatelyItem."""

    @staticmethod
    @abstractmethod
    def item_type() -> str:
        """Return the type of the item."""


class BaseTypeMapper(ABC):
    """
    TypeMapper is an interface that is implemented by Stately generated schema code
    unmarshalling concrete Stately schema from generic
    protobuf items that are received from the API.
    """

    @staticmethod
    @abstractmethod
    def unmarshal(item: PBItem) -> StatelyItem:
        """Unmarshal a generic protobuf item into a concrete schema type."""
