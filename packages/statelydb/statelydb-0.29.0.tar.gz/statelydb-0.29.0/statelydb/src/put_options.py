"""Options for a Put operation."""

from dataclasses import dataclass

from statelydb.src.types import StatelyItem


@dataclass
class WithPutOptions:
    """Wrap an item with additional options for a Put operation."""

    item: StatelyItem
    must_not_exist: bool
    """must_not_exist is a condition that indicates this item must not already
    exist at any of its key paths. If there is already an item at one of those
    paths, the Put operation will fail with a ConditionalCheckFailed error. Note
    that if the item has an `initialValue` field in its key, that initial value
    will automatically be chosen not to conflict with existing items, so this
    condition only applies to key paths that do not contain the `initialValue`
    field."""
    overwrite_metadata_timestamps: bool
    """If set to true, the server will set the `createdAtTime` and/or
    `lastModifiedAtTime` fields based on the current values in this item
    (assuming you've mapped them to a field using `fromMetadata`). Without this,
    those fields are always ignored and the server sets them to the appropriate
    times. This option can be useful when migrating data from another system."""
