"""Helpers for transactions."""

from __future__ import annotations

import asyncio
import contextlib
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Literal, TypeVar
from uuid import UUID

from google.protobuf import empty_pb2 as pb_empty
from grpclib.const import Status
from grpclib.exceptions import StreamTerminatedError
from typing_extensions import Self

from statelydb.lib.api.db import delete_pb2 as pb_delete
from statelydb.lib.api.db import get_pb2 as pb_get
from statelydb.lib.api.db import list_pb2 as pb_list
from statelydb.lib.api.db import put_pb2 as pb_put
from statelydb.lib.api.db import transaction_pb2 as pb_transaction
from statelydb.lib.api.db.list_pb2 import SortDirection
from statelydb.src.errors import StatelyError
from statelydb.src.list import (
    ListResult,
    TokenReceiver,
    build_filters,
    handle_list_response,
)
from statelydb.src.put_options import WithPutOptions
from statelydb.src.types import StatelyItem

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from types import TracebackType

    from grpclib.client import Stream

    from statelydb.lib.api.db.list_token_pb2 import ListToken
    from statelydb.src.types import BaseTypeMapper, SchemaID, SchemaVersionID, StoreID

T = TypeVar("T", bound=StatelyItem)
ResponseField = Literal["get_results", "put_ack", "list_results", "finished"]
ResponseType = TypeVar(
    "ResponseType",
    pb_transaction.TransactionGetResponse,
    pb_transaction.TransactionPutAck,
    pb_transaction.TransactionListResponse,
    pb_transaction.TransactionFinished,
)


class TransactionFailedError(Exception):
    """
    TransactionFailedError is the internal error that is raised when a transaction has
    failed due to an error raised by the server.

    In these cases all processing should be abandonded and the stream should be closed
    so that the Client._recv_trailing_metadata() hook can fire and raise the
    parsed error sent by the server.
    """


class TransactionResult:
    """
    The result of a transaction.
    This contains two fields, `puts` and `committed`.
    `puts` is a list of items that were put during the transaction.
    `committed` is a boolean indicating if the transaction was committed.
    """

    def __init__(
        self,
        puts: list[StatelyItem] | None = None,
        committed: bool = False,
    ) -> None:
        """
        Construct a new TransactionResult.

        :param puts: The list of items that were put during the transaction.
            Defaults to None.
        :type puts: list[StatelyItem], optional

        :param committed: Whether or not the transaction was committed.
            Defaults to False.
        :type committed: bool, optional
        """
        self.puts = puts or []
        self.committed = committed


class Transaction(
    AbstractAsyncContextManager["Transaction"],
):
    """
    The transaction context manager.
    This class is returned from the `transaction` method on the Stately client.
    """

    def __init__(
        self,
        store_id: StoreID,
        type_mapper: BaseTypeMapper,
        schema_id: SchemaID,
        schema_version_id: SchemaVersionID,
        stream: Stream[
            pb_transaction.TransactionRequest,
            pb_transaction.TransactionResponse,
        ],
    ) -> None:
        """
        Create a new Transaction context manager.

        :param store_id: The store ID for the transaction.
        :type store_id: StoreID

        :param type_mapper: The Stately generated schema mapper for converting generic
            Stately Items into concrete schema types.
        :type type_mapper: BaseTypeMapper

        :param schema_id: An optional SchemaID used to validate the given
            schema_id is bound to the store_id. If this is not provided, this
            check will be skipped.
        :type schema_id: SchemaID

        :param schema_version_id: The schema version ID used to generate the type
            mapper. This is used to ensure that the schema used by the client matches
            the schema used by the server.
        :type schema_version_id: SchemaVersionID

        :param stream: The bidirectional stream to use for the transaction.
        :type stream: Stream[pb_transaction.TransactionRequest, pb_transaction.TransactionResponse]

        """
        self.result = TransactionResult()
        self._stream = stream
        self._message_id = 1
        self._store_id = store_id
        self._type_mapper = type_mapper
        self._schema_id = schema_id
        self._schema_version_id = schema_version_id

    def _next_message_id(self) -> int:
        self._message_id += 1
        return self._message_id

    async def __aenter__(self) -> Self:
        """Called when entering the context manager."""
        await self._stream.__aenter__()
        await self._stream.send_message(
            pb_transaction.TransactionRequest(
                message_id=self._next_message_id(),
                begin=pb_transaction.TransactionBegin(
                    store_id=self._store_id,
                    schema_id=self._schema_id,
                    schema_version_id=self._schema_version_id,
                ),
            ),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Called when exiting the context manager."""
        # TransactionFailedError indicates that there will be an error
        # waiting in self._stream.__aexit__ so it's safe to ignore
        with contextlib.suppress(TransactionFailedError):
            if exc_type is not None:
                # if there was an exception then abort the transaction
                await self._abort()
            else:
                # if no error then commit the transaction
                self.result = await self._commit()

        # don't propagate provided exceptions into the stream or else it will
        # throw them instead of the expected stream error details from the server
        await self._stream.__aexit__(None, None, None)
        # Returning False here will re-raise the provided exception
        # which is desirable if self._stream.__aexit__ didn't throw
        return False

    async def get_batch(self, *key_paths: str) -> list[StatelyItem]:
        """
        get_batch retrieves multiple items by their full key paths. This will
        return the corresponding items that exist. Use begin_list instead if you
        want to retrieve multiple items but don't already know the full key
        paths of the items you want to get. You can get items of different types
        in a single get_batch - you will need to use `isinstance` to determine
        what item type each item is.

        :param *key_paths: The full key path of each item to load.
        :type *key_paths: str

        :return: The list of Items retrieved from the store. These are returned
            as generic StatelyItems and should be cast or narrowed to the
            correct type if you are using typed python.
        :rtype: list[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                items = await txn.get_batch(
                    "/jedi-luke/equipment-lightsaber", "/jedi-luke/equipment-cloak")
                for item in items:
                    if isinstance(item, Equipment):
                        print(f"Got an equipment item: {item}")

        """
        resp = await self._request_response(
            get_items=pb_transaction.TransactionGet(
                gets=[pb_get.GetItem(key_path=k) for k in key_paths],
            ),
            expect_field="get_results",
            expect_type=pb_transaction.TransactionGetResponse,
        )
        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def get(self, item_type: type[T], key_path: str) -> T | None:
        """
        get retrieves an item by its full key path.

        :param item_type: One of the itemType names from your schema. This is
                used to determine the type of the resulting item.
        :type item_type: type[T]

        :param key_path: The full key path of the item.
        :type key_path: str

        :return: The Stately Item retrieved from the store or None if no item
            was found.
        :rtype: T | None

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                item = await txn.get(Equipment, "/jedi-luke/equipment-lightsaber")
                if item is not None:
                    print(f"Got an equipment item: {item}")

        """
        resp = await self.get_batch(key_path)
        if len(resp) == 0:
            return None
        item = next(iter(resp))
        if item.item_type() != item_type.item_type():
            msg = f"Expected item type {item_type.item_type()}, got {item.item_type()}"
            raise StatelyError(
                stately_code="Internal",
                message=msg,
                code=Status.INTERNAL,
            )
        if not isinstance(item, item_type):
            msg = f"Error unmarshalling {item_type}, got {type(item)}"
            raise StatelyError(
                stately_code="Internal",
                message=msg,
                code=Status.INTERNAL,
            )
        return item

    async def put(
        self,
        item: StatelyItem,
        must_not_exist: bool = False,
        overwrite_metadata_timestamps: bool = False,
    ) -> int | UUID | None:
        """
        put adds an Item to the Store, or replaces the Item if it already exists
        at that path. Unlike the put method outside of a transaction, this only
        returns the generated ID of the item, and then only if the item was
        newly created and has an `initialValue` field in its key. This is so you
        can use that ID in subsequent puts to reference newly created items. The
        final put items will not be returned until the transaction is committed,
        in which case they will be included in the `TransactionResult.puts`
        list.

        :param item: The item to put.
        :param must_not_exist: This is a condition that indicates this item must
            not already exist at any of its key paths. If there is already an
            item at one of those paths, the Put operation will fail with a
            ConditionalCheckFailed error. Note that if the item has an
            `initialValue` field in its key, that initial value will
            automatically be chosen not to conflict with existing items, so this
            condition only applies to key paths that do not contain the
            `initialValue` field.
        :param overwrite_metadata_timestamps: If set to True, the server will
            set the `createdAtTime` and/or `lastModifiedAtTime` fields based on
            the current values in this item (assuming you've mapped them to a
            field using `fromMetadata`). Without this, those fields are always
            ignored and the server sets them to the appropriate times. This
            option can be useful when migrating data from another system.
        :type item: StatelyItem

        :return: A generated IDs for the item, if that item had an ID generated
            for its "initialValue" field. Otherwise the value is None. This
            value can be used in subsequent puts to reference newly created
            items.
        :rtype: int | UUID | None

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            with txn:
                lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
                lightsaber_id = await txn.put(lightsaber)
            assert txn.result.committed
            assert len(tnx.result.puts) == 1

        """
        return next(
            iter(
                await self.put_batch(
                    WithPutOptions(item, must_not_exist, overwrite_metadata_timestamps)
                )
            )
        )

    async def put_batch(
        self, *items: StatelyItem | WithPutOptions
    ) -> list[int | UUID | None]:
        """
        put_batch adds multiple Items to the Store, or replaces Items if they
        already exist at that path. You can put items of different types in a
        single put_batch. Unlike the put_batch method outside of a transaction,
        this only returns the generated IDs of the items, and then only if the
        item was newly created and has an `initialValue` field in its key. The
        IDs are returned in the same order as the inputs. This is so you can use
        that ID in subsequent puts to reference newly created items. The final
        put items will not be returned until the transaction is committed, in
        which case they will be included in the `TransactionResult.puts` list.

        :param *items: Items from your generated schema.
        :type *items: StatelyItem

        :return: An array of generated IDs for each item, if that item had an ID
            generated for its "initialValue" field. Otherwise the value is None.
            These are returned in the same order as the input items. This value
            can be used in subsequent puts to reference newly created items.
        :rtype: list[int | UUID | None]

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            with txn:
                lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
                cloak = Equipment(color="brown", jedi="luke", type="cloak")
                lightsaber_id, cloak_id = await txn.put_batch(lightsaber, cloak)
            assert txn.result.committed
            assert len(tnx.result.puts) == 2

        """
        puts = [
            (
                pb_put.PutItem(
                    item=i.item.marshal(),
                    must_not_exist=i.must_not_exist,
                    overwrite_metadata_timestamps=i.overwrite_metadata_timestamps,
                )
                if isinstance(i, WithPutOptions)
                else pb_put.PutItem(item=i.marshal())
            )
            for i in items
        ]
        resp = await self._request_response(
            put_items=pb_transaction.TransactionPut(
                puts=puts,
            ),
            expect_field="put_ack",
            expect_type=pb_transaction.TransactionPutAck,
        )

        out: list[int | UUID | None] = []
        for i in resp.generated_ids:
            if i.WhichOneof("value") == "uint":
                out.append(i.uint)
            elif i.WhichOneof("value") == "bytes":
                out.append(UUID(bytes=i.bytes))
            else:
                out.append(None)
        return out

    async def delete(self, *key_paths: str) -> None:
        """
        delete removes one or more items from the Store by their full key paths.
        delete succeeds even if there isn't an item at that key path.

        :param *key_paths: The full key paths of the items.
        :type *key_paths: str

        :return: None

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                await txn.delete("/jedi-luke/equipment-lightsaber")

        """
        await self._request_only(
            delete_items=pb_transaction.TransactionDelete(
                deletes=[pb_delete.DeleteItem(key_path=k) for k in key_paths],
            ),
        )

    async def begin_list(
        self,
        key_path_prefix: str,
        limit: int = 0,
        sort_direction: SortDirection = SortDirection.SORT_ASCENDING,
        item_types: list[type[StatelyItem] | str] | None = None,
        cel_filters: list[tuple[type[StatelyItem] | str, str]] | None = None,
        gt: str | None = None,
        lt: str | None = None,
        gte: str | None = None,
        lte: str | None = None,
    ) -> ListResult[StatelyItem]:
        """
        begin_list retrieves Items that start with a specified key_path_prefix
        from a single Group. Because it can only list items from a single Group,
        the key path prefix must at least start with a full Group Key (a single
        key segment with a namespace and an ID, e.g. `/user-1234`).

        begin_list will return an empty result set if there are no items
        matching that key prefix. This API returns a token that you can pass to
        continue_list to expand the result set.

        begin_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can list items of different types in a single begin_list, and you
        can use `isinstance` to handle different item types.

        :param key_path_prefix: The key path prefix to query for. It must be at
            least a full Group Key (e.g. `/user-1234`).
        :type key_path_prefix: str

        :param limit: The max number of Items to retrieve. Defaults to 0 which
            fetches all Items.
        :type limit: int, optional

        :param sort_direction: The direction to sort results. Defaults to
            SortDirection.SORT_ASCENDING.
        :type sort_direction: SortDirection, optional

        :param item_types: The item types to filter by. If not provided, all
            item types will be returned.
        :type item_types: list[type[T] | str], optional

        :param cel_filters: An optional list of (item type, CEL expressions)
            tuples to filter the results set by.

            CEL expressions are only evaluated for the item type they are
            defined for, and do not affect other item types in the result set.
            This means if an item type has no CEL filter and there are no
            item_type filters constraints, it will be included in the result
            set.

            In the context of a CEL expression, the key-word `this` refers to
            the item being evaluated, and property properties should be accessed
            by the names as they appear in schema -- not necessarily as they
            appear in the generated code for a particular language. For example,
            if you have a `Movie` item type with the property `rating`, you
            could write a CEL expression like `this.rating == 'R'` to return
            only movies that are rated `R`.

            Find the full CEL language definition here:
            https://github.com/google/cel-spec/blob/master/doc/langdef.md
        :type cel_filters: list[tuple[type[T] | str, str]], optional

        :param gt: An optional key path to filter results to only include items
            with a key greater than the specified value based on lexicographic
            ordering. Defaults to None.
        :type gt: str, optional

        :param lt: An optional key path to filter results to only include items
            with a key less than the specified value based on lexicographic
            ordering. Defaults to None.
        :type lt: str, optional

        :param gte: An optional key path to filter results to only include items
            with a key greater than or equal to the specified value based on
            lexicographic ordering. Defaults to None.
        :type gte: str, optional

        :param lte: An optional key path to filter results to only include items
            with a key less than or equal to the specified value based on
            lexicographic ordering. Defaults to None.
        :type lte: str, optional

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                list_resp = await txn.begin_list("/jedi-luke/equipment")
                async for item in list_resp:
                    if isinstance(item, Equipment):
                        print(item.color)
                token = list_resp.token

        """
        # Build key conditions for gt, gte, lt, lte
        ops = [
            (gt, pb_list.OPERATOR_GREATER_THAN),
            (gte, pb_list.OPERATOR_GREATER_THAN_OR_EQUAL),
            (lt, pb_list.OPERATOR_LESS_THAN),
            (lte, pb_list.OPERATOR_LESS_THAN_OR_EQUAL),
        ]
        kcs = [
            pb_list.KeyCondition(operator=op, key_path=val)
            for val, op in ops
            if val is not None
        ]
        msg_id = await self._request_only(
            begin_list=pb_transaction.TransactionBeginList(
                key_path_prefix=key_path_prefix,
                limit=limit,
                sort_direction=sort_direction,
                filter_conditions=build_filters(item_types, cel_filters),
                key_conditions=kcs,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(
                self._type_mapper,
                token_receiver,
                self._stream_list_responses(msg_id),
            ),
        )

    async def continue_list(self, token: ListToken) -> ListResult[StatelyItem]:
        """
        continue_list takes the token from a begin_list call and returns the
        next "page" of results based on the original query parameters and
        pagination options. It doesn't have options because it is a continuation
        of a previous list operation. It will return a new token which can be
        used for another continue_list call, and so on. The token is the same
        one used by sync_list - each time you call either continue_list or
        sync_list, you should pass the latest version of the token, and the
        result will include a new version of the token to use in subsequent
        calls. You may interleave continue_list and sync_list calls however you
        like, but it does not make sense to make both calls in parallel. Calls
        to continue_list are tied to the authorization of the original
        begin_list call, so if the original begin_list call was allowed,
        continue_list with its token should also be allowed.

        continue_list streams results via an AsyncGenerator, allowing you to
        handle results as they arrive. You can call `collect()` on the results to
        get all the results as a list if you'd rather wait for everything first.

        You can list items of different types in a single continueList, and you can
        use `isinstance` to handle different item types.

        :param token: The token from the previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            with await client.transaction() as txn:
                list_resp = await txn.begin_list("/jedi-luke/equipment")
                async for item in list_resp:
                    if isinstance(item, Equipment):
                        print(item.color)
                token = list_resp.token
                while token.can_continue:
                    list_resp = await txn.continue_list(token)
                    async for item in list_resp:
                        if isinstance(item, Equipment):
                            print(item)
                    token = list_resp.token

        """
        msg_id = await self._request_only(
            continue_list=pb_transaction.TransactionContinueList(
                token_data=token.token_data,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(
                self._type_mapper,
                token_receiver,
                self._stream_list_responses(msg_id),
            ),
        )

    async def _commit(self) -> TransactionResult:
        """
        _commit finalizes the transaction, applying all the changes made within it.
        This is called automatically if the context manager runs without
        error.
        """
        resp = await self._request_response(
            commit=pb_empty.Empty(),
            expect_field="finished",
            expect_type=pb_transaction.TransactionFinished,
        )
        return TransactionResult(
            puts=[self._type_mapper.unmarshal(i) for i in resp.put_results],
            committed=resp.committed,
        )

    async def _abort(self) -> None:
        """
        _abort cancels the transaction, discarding all changes made within it. This
        is called automatically if the context manager throws an error.
        """
        await self._request_response(
            abort=pb_empty.Empty(),
            expect_field="finished",
            expect_type=pb_transaction.TransactionFinished,
        )

    async def _request_only(
        self,
        begin: pb_transaction.TransactionBegin | None = None,
        get_items: pb_transaction.TransactionGet | None = None,
        begin_list: pb_transaction.TransactionBeginList | None = None,
        continue_list: pb_transaction.TransactionContinueList | None = None,
        put_items: pb_transaction.TransactionPut | None = None,
        delete_items: pb_transaction.TransactionDelete | None = None,
        commit: pb_empty.Empty | None = None,
        abort: pb_empty.Empty | None = None,
    ) -> int:
        """
        Helper to dispatch requests to the transaction stream.

        :return: The generated message ID of the request.
        :rtype: int
        """
        msg_id = self._next_message_id()
        await self._stream.send_message(
            pb_transaction.TransactionRequest(
                message_id=msg_id,
                begin=begin,
                get_items=get_items,
                begin_list=begin_list,
                continue_list=continue_list,
                put_items=put_items,
                delete_items=delete_items,
                commit=commit,
                abort=abort,
            ),
            # grpclib stream needs to know if the stream is expected to
            # end after this message
            end=commit is not None or abort is not None,
        )
        return msg_id

    async def _expect_response(
        self,
        message_id: int,
        expect_field: ResponseField,
        expect_type: type[ResponseType],
    ) -> ResponseType:
        """
        Helper to wait for an incoming response from the transaction stream.
        This will raise an error if the response does not match the expected
        message ID, or if it cannot be unpacked as expected.
        """
        try:
            resp = await self._stream.recv_message()
        except StreamTerminatedError as e:
            raise StatelyError(
                stately_code="StreamClosed",
                code=Status.FAILED_PRECONDITION,
                message="Transaction failed due to server stream termination",
                cause=e,
            ) from None
        except asyncio.CancelledError:
            # if the event loop was cancelled then re-raise the error
            # to trigger an abort.
            # first wait for the expected response so that the message_id
            # order is preserved - otherwise abort will get the response
            # that was expected in this function
            _ = await self._stream.recv_message()
            raise

        if resp is None:
            msg = "Received unexpected None on stream."
            raise TransactionFailedError(msg)
        if resp.message_id != message_id:
            msg = f"Transaction expected message_id {message_id}, got {resp.message_id}"
            raise StatelyError(
                stately_code="Internal",
                message=msg,
                code=Status.INTERNAL,
            )
        if resp.WhichOneof("result") != expect_field:
            msg = (
                f"Transaction expected result type: {expect_field}, "
                f"got {resp.WhichOneof('result')}"
            )
            raise StatelyError(
                stately_code="Internal",
                message=msg,
                code=Status.INTERNAL,
            )
        val = getattr(resp, expect_field)
        if not isinstance(val, expect_type):
            msg = (
                f"Transaction expected field {expect_field} to have "
                f"type {expect_type}, got type {type(val)}"
            )
            raise StatelyError(
                stately_code="Internal",
                message=msg,
                code=Status.INTERNAL,
            )
        return val

    async def _request_response(
        self,
        expect_field: ResponseField,
        expect_type: type[ResponseType],
        begin: pb_transaction.TransactionBegin | None = None,
        get_items: pb_transaction.TransactionGet | None = None,
        begin_list: pb_transaction.TransactionBeginList | None = None,
        continue_list: pb_transaction.TransactionContinueList | None = None,
        put_items: pb_transaction.TransactionPut | None = None,
        delete_items: pb_transaction.TransactionDelete | None = None,
        commit: pb_empty.Empty | None = None,
        abort: pb_empty.Empty | None = None,
    ) -> ResponseType:
        """A helper that sends an input command, then waits for an output result."""
        msg_id = await self._request_only(
            begin=begin,
            get_items=get_items,
            begin_list=begin_list,
            continue_list=continue_list,
            put_items=put_items,
            delete_items=delete_items,
            commit=commit,
            abort=abort,
        )

        return await self._expect_response(msg_id, expect_field, expect_type)

    async def _stream_list_responses(
        self,
        message_id: int,
    ) -> AsyncGenerator[pb_transaction.TransactionListResponse]:
        """Convert a stream of list responses into a generator of items."""
        while True:
            yield await self._expect_response(
                message_id,
                "list_results",
                pb_transaction.TransactionListResponse,
            )
