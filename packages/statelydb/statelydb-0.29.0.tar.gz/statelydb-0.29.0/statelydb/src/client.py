"""The Stately Python client."""

from __future__ import annotations

import contextlib
import copy
from functools import cached_property
from typing import TYPE_CHECKING, Callable, TypeVar

from grpclib.const import Status
from typing_extensions import Self, TypedDict

from statelydb.lib.api.db import continue_list_pb2 as pb_continue_list
from statelydb.lib.api.db import continue_scan_pb2 as pb_continue_scan
from statelydb.lib.api.db import delete_pb2 as pb_delete
from statelydb.lib.api.db import get_pb2 as pb_get
from statelydb.lib.api.db import list_pb2 as pb_list
from statelydb.lib.api.db import put_pb2 as pb_put
from statelydb.lib.api.db import scan_pb2 as pb_scan
from statelydb.lib.api.db import service_grpc as db
from statelydb.lib.api.db import sync_list_pb2 as pb_sync_list
from statelydb.lib.api.db.list_pb2 import SortDirection
from statelydb.src.auth import (
    AuthTokenProvider,
    init_server_auth,
)
from statelydb.src.channel import StatelyChannel
from statelydb.src.errors import StatelyError
from statelydb.src.list import (
    ListResult,
    TokenReceiver,
    build_filters,
    handle_list_response,
)
from statelydb.src.put_options import WithPutOptions
from statelydb.src.sync import handle_sync_response
from statelydb.src.transaction import Transaction
from statelydb.src.types import StatelyItem, Stopper

if TYPE_CHECKING:
    from statelydb.lib.api.db.list_token_pb2 import ListToken
    from statelydb.src.sync import SyncResult
    from statelydb.src.types import BaseTypeMapper, SchemaID, SchemaVersionID, StoreID

T = TypeVar("T", bound=StatelyItem)


class ClientArgs(TypedDict, total=False):
    """
    A type helper for the keyword arguments to the generated Client
    constructor.
    """

    token_provider: Callable[[str], AuthTokenProvider]
    token_provider_stopper: Stopper
    endpoint: str
    region: str
    no_auth: bool


class Client:
    """Client is a Stately client that interacts with the given store."""

    _endpoint: str
    _token_provider: AuthTokenProvider | None
    _token_provider_stopper: Stopper | None
    _store_id: StoreID
    _schema_version_id: SchemaVersionID
    _schema_id: SchemaID
    _type_mapper: BaseTypeMapper
    _allow_stale: bool
    _channel: StatelyChannel | None = None

    def __init__(
        self,
        store_id: StoreID,
        type_mapper: BaseTypeMapper,
        schema_id: SchemaID,
        schema_version_id: SchemaVersionID,
        token_provider: Callable[[str], AuthTokenProvider] | None = None,
        token_provider_stopper: Stopper | None = None,
        endpoint: str | None = None,
        region: str | None = None,
        no_auth: bool = False,
    ) -> None:
        """
        Construct a new Stately Client.

        :param store_id: The ID of the store to connect to. All client
            operations will be performed on this store.
        :type store_id: StoreID

        :param type_mapper: The Stately generated schema mapper for converting
            generic Stately Items into concrete schema types.
        :type type_mapper: BaseTypeMapper

        :param schema_id: An optional SchemaID used to validate the given
            schema_id is bound to the store_id. If this is not provided, this
            check will be skipped.
        :type schema_id: SchemaID

        :param schema_version_id: The schema version ID used to generate the
            type mapper. This is used to ensure that the schema used by the
            client matches the schema used by the server.
        :type schema_version_id: SchemaVersionID

        :param token_provider: An optional auth token provider. Defaults to
            reading `STATELY_CLIENT_ID` and `STATELY_CLIENT_SECRET` from the
            environment.
        :type token_provider: Callable[[str], AuthTokenProvider], optional

        :param token_provider_stopper: An optional stopper function for the
            token provider. This is used to stop the token provider when the
            client is closed. Defaults to None.

        :param endpoint: The Stately API endpoint to connect to. Defaults to
            "https://api.stately.cloud" if no region is provided.
        :type endpoint: str, optional

        :param region: The Stately region to connect to. If region is provided
            and endpoint is not provided then the regional endpoint will be
            used.
        :type region: str, optional

        :param no_auth: Indicates that the client should not attempt to get an
            auth token. This is used when talking to the Stately BYOC Data Plane
            on localhost.
        :type no_auth: bool, optional

        :return: A Client for interacting with a Stately store
        :rtype: Client
        """
        self._endpoint = Client._make_endpoint(endpoint=endpoint, region=region)
        if not no_auth:
            if token_provider:
                self._token_provider = token_provider(self._endpoint)
                self._token_provider_stopper = token_provider_stopper
            else:
                token_provider, self._token_provider_stopper = init_server_auth()
                self._token_provider = token_provider(self._endpoint)

        self._store_id = store_id
        self._schema_id = schema_id
        self._schema_version_id = schema_version_id
        self._type_mapper = type_mapper
        self._allow_stale = False

    # This cached_property decorator is required so that the client can be constructed
    # within a sync context. This can be removed when the following issue is resolved:
    # https://github.com/vmagamedov/grpclib/issues/161
    @cached_property
    def _db_service(self) -> db.DatabaseServiceStub:
        self._channel = StatelyChannel(endpoint=self._endpoint)

        if self._token_provider:
            self._channel = self._channel.with_auth(token_provider=self._token_provider)
        return db.DatabaseServiceStub(self._channel)

    @staticmethod
    def _make_endpoint(endpoint: str | None = None, region: str | None = None) -> str:
        """
        Resolve the Stately API endpoint based on the provided endpoint and region.

        :param endpoint: The Stately API endpoint to connect to.
            Defaults to "https://api.stately.cloud" if no region is provided.
        :type endpoint: str, optional

        :param region: The Stately region to connect to.
            If region is provided and endpoint is not provided then the regional
            endpoint will be used.

        :return: The resolved Stately API endpoint.
        :rtype: str
        """
        if endpoint:
            return endpoint
        if region is None:
            return "https://api.stately.cloud"

        if region.startswith("aws-"):
            region = region.removeprefix("aws-")
        return f"https://{region}.aws.api.stately.cloud"

    async def close(self) -> None:
        """
        Close the client and any underlying resources.
        This doesn't have any async code but _channel.close() requires that it is
        called from the same async context that it was created in, so we make
        it an async method to try and ensure that.
        """
        if self._token_provider_stopper is not None:
            self._token_provider_stopper()
        if self._channel is not None:
            # you hit a runtime error if the event loop is already closed.
            # i think it is safe to ignore this.
            with contextlib.suppress(RuntimeError):
                self._channel.close()

    def with_allow_stale(self, allow_stale: bool = True) -> Self:
        """
        Returns a new client that is either OK with or not OK with stale reads.
        This affects get and list operations from the returned client. Use this
        only if you know you can tolerate stale reads. This can result in improved
        performance, availability, and cost.

        :param allow_stale: Whether staleness is allowed or not. Defaults to True.
        :type allow_stale: bool, optional

        :return: A clone of the existing client with allow_stale set to the new value.
        :rtype: Self
        """
        # Create a shallow copy since we don't mind if the grpc client,
        # type mapper or token provider are shared.
        # These are all safe for concurrent use.
        new_client = copy.copy(self)
        new_client._allow_stale = allow_stale  # noqa: SLF001
        return new_client

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
            item = await client.get(Equipment, "/jedi-luke/equipment-lightsaber")

        """
        resp = await self.get_batch(key_path)
        if len(resp) == 0:
            return None
        item = next(iter(resp))
        if item.item_type() != item_type.item_type():
            msg = (
                f"Get returned item type {item.item_type()}. "
                f"Expected item type {item_type.item_type()}"
            )
            raise StatelyError(
                message=msg,
                code=Status.INTERNAL,
                stately_code="Internal",
            )
        if not isinstance(item, item_type):
            msg = (
                "Error unmarshalling get response."
                f"Unmarshaler returned {type(item)} instead of {item_type}"
            )
            raise StatelyError(
                message=msg,
                code=Status.INTERNAL,
                stately_code="Internal",
            )
        return item

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
            first_item, second_item = await client.get_batch(
                "/jedi-luke/equipment-lightsaber", "/jedi-luke/equipment-cloak")
            print(cast(Equipment, first_item).color)
            if isinstance(second_item, Equipment):
                print(second_item.color)

        """
        resp = await self._db_service.Get(
            pb_get.GetRequest(
                store_id=self._store_id,
                gets=[
                    pb_get.GetItem(
                        key_path=key_path,
                    )
                    for key_path in key_paths
                ],
                allow_stale=self._allow_stale,
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )
        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def put(
        self,
        item: T,
        must_not_exist: bool = False,
        overwrite_metadata_timestamps: bool = False,
    ) -> T:
        """
        put adds an Item to the Store, or replaces the Item if it already exists
        at that path.

        This call will fail if:
            - The Item conflicts with an existing Item at the same path and the
              must_not_exist option is set, or the item's ID will be chosen with
              an `initialValue` and one of its other key paths conflicts with an
              existing item.

        :param item: An Item from your generated schema.
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
        :type item: T

        :return: The item that was put, with any server-generated fields filled
        in.

        Examples
        --------
        .. code-block:: python
            lightsaber = Equipment(color="green", jedi="luke", type="lightsaber")
            lightsaber = await client.put(lightsaber)
            # With options:
            lightsaber = await client.put(lightsaber, must_not_exist=True)

        """
        put_item = next(
            iter(
                await self.put_batch(
                    WithPutOptions(item, must_not_exist, overwrite_metadata_timestamps)
                )
            )
        )
        if put_item.item_type() != item.item_type():
            msg = (
                f"Put returned item type {put_item.item_type()}. "
                f"Expected item type {item.item_type()}"
            )
            raise StatelyError(
                message=msg,
                code=Status.INTERNAL,
                stately_code="Internal",
            )
        if isinstance(put_item, type(item)):
            return put_item
        msg = (
            "Error unmarshalling put response."
            f"Unmarshaler returned {type(put_item)} instead of {type(item)}"
        )
        raise StatelyError(
            message=msg,
            code=Status.INTERNAL,
            stately_code="Internal",
        )

    async def put_batch(
        self, *items: StatelyItem | WithPutOptions
    ) -> list[StatelyItem]:
        """
        put_batch adds multiple Items to the Store, or replaces Items if they
        already exist at that path. You can put items of different types in a
        single put_batch. All puts in the request are applied atomically - there
        are no partial successes.

        This will fail if:
            - Any Item conflicts with an existing Item at the same path and its
             must_not_exist option is set, or the item's ID will be chosen with
             an `initialValue` and one of its other key paths conflicts with an
             existing item.

        :param *items: Items from your generated schema.
        :type *items: StatelyItem

        :return: The items that were put, with any server-generated fields
            filled in. They are returned in the same order they were provided.
        :rtype: list[StatelyItem]

        Examples
        --------
        .. code-block:: python
            items = await client.put_batch(
                Equipment(color="green", jedi="luke", type="lightsaber"),
                Equipment(color="brown", jedi="luke", type="cloak"),
            )
            # With options:
            items = await client.put_batch(
                WithPutOptions(item=item, must_not_exist=True),
                cloak,
            )

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
        resp = await self._db_service.Put(
            pb_put.PutRequest(
                store_id=self._store_id,
                puts=puts,
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )

        return [self._type_mapper.unmarshal(i) for i in resp.items]

    async def delete(self, *key_paths: str) -> None:
        """
        delete removes one or more items from the Store by their full key paths.
        delete succeeds even if there isn't an item at that key path. Tombstones
        will be saved for deleted items for some time, so that sync_list can
        return information about deleted items. Deletes are always applied
        atomically; all will fail or all will succeed.

        :param *key_paths: The full key paths of the items.
        :type *key_paths: str

        :return: None

        Examples
        --------
        .. code-block:: python
            await client.delete("/jedi-luke/equipment-lightsaber")

        """
        await self._db_service.Delete(
            pb_delete.DeleteRequest(
                store_id=self._store_id,
                deletes=[
                    pb_delete.DeleteItem(key_path=key_path) for key_path in key_paths
                ],
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
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
        continue_list to expand the result set, or to sync_list to get updates
        within the result set.

        begin_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on it to get all the
        results as a list.

        You can list items of different types in a single begin_list, and you
        can use `isinstance` to handle different item types.

        :param key_path_prefix: The key path prefix to query for. It must be at
            least a full Group Key (e.g. `/user-1234`).
        :type key_path_prefix: str

        :param limit: The max number of items to retrieve. If set to 0 then the
            full set will be returned. Defaults to 0.
        :type limit: int, optional

        :param sort_direction: The direction to sort the results. Defaults to
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
            list_resp = await client.begin_list("/jedi-luke")
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
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

        # grpclib only supports streaming with a context manager but that doesn't work
        # here because we want to wrap the stream and return it to the customer for them
        # to read at their leisure.
        # To get around that we have to manually call __aenter__ and __aexit__ hooks on
        # the stream.
        # We call __aenter__ here to open the thing and call __aexit__ at the end of the
        # response handler to ensure the stream is closed correctly.
        stream = self._db_service.BeginList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_list.BeginListRequest(
                store_id=self._store_id,
                key_path_prefix=key_path_prefix,
                limit=limit,
                sort_direction=sort_direction,
                schema_id=self._schema_id,
                filter_conditions=build_filters(item_types, cel_filters),
                key_conditions=kcs,
                schema_version_id=self._schema_version_id,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
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

        You can list items of different types in a single continue_list, and you
        can use `isinstance` to handle different item types.

        :param token: The latest token from a previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            list_resp = await client.continue_list(token)
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
            token = list_resp.token

        """
        stream = self._db_service.ContinueList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_continue_list.ContinueListRequest(
                token_data=token.token_data,
                direction=pb_continue_list.CONTINUE_LIST_FORWARD,
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
        )

    async def sync_list(self, token: ListToken) -> ListResult[SyncResult]:
        """
        sync_list returns all changes to Items within the result set of a
        previous List operation. For all Items within the result set that were
        modified, it returns the full Item at in its current state. If the
        result set has already been expanded to the end (in the direction of the
        original begin_list request), sync_list will return newly created Items
        as well. It also returns a list of Item key paths that were deleted
        since the last sync_list, which you should reconcile with your view of
        items returned from previous begin_list/continue_list calls. Using this
        API, you can start with an initial set of items from begin_list, and
        then stay up to date on any changes via repeated sync_list requests over
        time.

        The token is the same one used by continue_list - each time you call
        either continue_list or sync_list, you should pass the latest version of
        the token, and then use the new token from the result in subsequent
        calls. You may interleave continue_list and sync_list calls however you
        like, but it does not make sense to make both calls in parallel. Calls
        to sync_list are tied to the authorization of the original begin_list
        call, so if the original begin_list call was allowed, sync_list with its
        token should also be allowed.

        sync_list streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on the results to get all
        the results as a list if you'd rather wait for everything first.

        Each result will be one of the following types:
            - SyncChangedItem: An item that was changed or added since the last
              sync_list call.
            - SyncDeletedItem: The key path of an item that was deleted since
              the last sync_list call.
            - SyncUpdatedItemKeyOutsideListWindow: An item that was updated but
              is not within the current result set. You can treat this like
              SyncDeletedItem, but the item hasn't actually been deleted, it's
              just not part of your view of the list anymore.
            - SyncReset: A reset signal that indicates any previously cached
              view of the result set is no longer valid. You should throw away
              any locally cached data. This will always be followed by a series
              of SyncChangedItem that make up a new view of the result set.

        :param token: The latest token from a previous list operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[SyncResult]

        Examples
        --------
        .. code-block:: python
            sync_resp = await client.sync_list(token)
            async for item in sync_resp:
                if isinstance(item, SyncChangedItem):
                    print(item.item)
                elif isinstance(item, SyncDeletedItem):
                    print(item.key_path)
                elif isinstance(item, SyncUpdatedItemKeyOutsideListWindow):
                    print(item.key_path)
            token = sync_resp.token

        """
        stream = self._db_service.SyncList.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_sync_list.SyncListRequest(
                token_data=token.token_data,
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_sync_response(self._type_mapper, token_receiver, stream),
        )

    async def begin_scan(
        self,
        limit: int = 0,
        item_types: list[type[StatelyItem] | str] | None = None,
        cel_filters: list[tuple[type[StatelyItem] | str, str]] | None = None,
        total_segments: int | None = None,
        segment_index: int | None = None,
    ) -> ListResult[StatelyItem]:
        """
        begin_scan initiates a scan request which will scan over the entire
        store and apply the provided filters. This API returns a token that you
        can pass to continue_scan to paginate through the result set.

        begin_scan streams results via an AsyncGenerator, allowing you to handle
        results as they arrive. You can call `collect()` on the results to get all
        the results as a list if you'd rather wait for everything first.

        begin_scan can return items of many types, and you can use `isinstance`
        to handle different item types.

        WARNING: THIS API CAN BE EXPENSIVE FOR STORES WITH A LARGE NUMBER OF
        ITEMS.

        :param limit: The max number of items to retrieve. If set to 0 then the
            first page of results will be returned which may empty because it
            does not contain items of your selected item types. Be sure to check
            token.can_continue to see if there are more results to fetch.
            Defaults to 0.
        :type limit: int, optional

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

        :param total_segments: The total number of segments to divide the scan
            into. Use this when you want to parallelize your operation. Defaults
            to None.
        :type total_segments: int, optional

        :param segment_index: The index of the segment to scan. Use this when
            you want to parallelize your operation. Defaults to None.
        :type segment_index: int, optional

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            list_resp = await client.begin_scan()
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
            token = list_resp.token

        """
        if total_segments is None != segment_index is None:
            msg = "total_segments and segment_index must both be set or both be None"
            raise StatelyError(
                stately_code="InvalidArgument",
                message=msg,
                code=Status.INVALID_ARGUMENT,
            )

        # grpclib only supports streaming with a context manager but that doesn't work
        # here because we want to wrap the stream and return it to the customer for them
        # to read at their leisure.
        # To get around that we have to manually call __aenter__ and __aexit__ hooks on
        # the stream.
        # We call __aenter__ here to open the thing and call __aexit__ at the end of the
        # response handler to ensure the stream is closed correctly.
        stream = self._db_service.BeginScan.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_scan.BeginScanRequest(
                store_id=self._store_id,
                limit=limit,
                filter_conditions=build_filters(item_types, cel_filters),
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
        )

    async def continue_scan(self, token: ListToken) -> ListResult[StatelyItem]:
        """
        continue_scan takes the token from a begin_scan call and returns the
        next "page" of results based on the original query parameters and
        pagination options.

        continue_scan streams results via an AsyncGenerator, allowing you to
        handle results as they arrive. You can call `collect()` on the results to
        get all the results as a list if you'd rather wait for everything first.

        You can scan items of different types in a single continue_scan, and you
        can use `isinstance` to handle different item types.

        :param token: The token from the previous scan operation.
        :type token: ListToken

        :return: The result generator.
        :rtype: ListResult[StatelyItem]

        Examples
        --------
        .. code-block:: python
            list_resp = await client.continue_scan(token)
            async for item in list_resp:
                if isinstance(item, Equipment):
                    print(item.color)
                else:
                    print(item)
            token = list_resp.token

        """
        stream = self._db_service.ContinueScan.open()
        await stream.__aenter__()
        await stream.send_message(
            pb_continue_scan.ContinueScanRequest(
                token_data=token.token_data,
                schema_id=self._schema_id,
                schema_version_id=self._schema_version_id,
            ),
        )
        token_receiver = TokenReceiver(token=None)
        return ListResult(
            token_receiver,
            handle_list_response(self._type_mapper, token_receiver, stream),
        )

    async def transaction(self) -> Transaction:
        """
        transaction allows you to issue reads and writes in any order, and all
        writes will either succeed or all will fail when the transaction
        finishes. It should by used with an `async with` block to ensure that
        the transaction is properly cleaned up.

        Reads are guaranteed to reflect the state as of when the transaction
        started. A transaction may fail if another transaction commits before
        this one finishes - in that case, you should retry your transaction.

        If any error is thrown from the with block, the transaction is aborted
        and none of the changes made in it will be applied. If the handler
        returns without error, the transaction is automatically committed.

        If any of the operations in the with block fails (e.g. a request is
        invalid) you may not find out until the *next* operation, or once the
        block finishes, due to some technicalities about how requests are
        handled.

        When the transaction is committed, the result property will contain the
        full version of any items that were put in the transaction, and the
        committed property will be True. If the transaction was aborted, the
        committed property will be False.

        :return: A new Transaction context manager.
        :rtype: Transaction

        Examples
        --------
        .. code-block:: python
            txn = await client.transaction()
            async with txn:
                item = await txn.get(Equipment, "/jedi-luke/equipment-lightsaber")
                if item is not None and item.color == "red":
                    item.color = "green"
                    await txn.put(item)
            assert txn.result.committed
            assert len(txn.puts) == 1

        """
        stream = self._db_service.Transaction.open()
        return Transaction(
            self._store_id,
            self._type_mapper,
            self._schema_id,
            self._schema_version_id,
            stream,
        )
