from dataclasses import dataclass
from .domain import ChangeEvent, Aggregate, Value
from typing import Protocol, Any


class ConcurrenceError(Exception):
    """An aggregate has been modified at the same time by several clients"""


@dataclass
class Version:
    value: int
    timestamp: int  # in ms


@dataclass
class EventRecord:
    version: Version
    event: ChangeEvent


class EventStore(Protocol):
    """Interface to manage aggregate events at persistence layer"""

    async def list_versions(self, key: str) -> list[Version]:
        ...

    async def load_event_records_chunk(
        self, key: str, chunk_version_number: int | None = None
    ) -> list[EventRecord]:
        ...

    async def append_event_records(self, key: str, event_records: list[EventRecord]):
        """Append event records to last chunk"""
        ...

    async def split_chunk(self, key: str, chunk_version_number: int):
        """Divide an already exist chunk into two"""
        ...

    async def remove_last_event_records_chunk(self, key: str):
        """Remove last chunk of events"""
        ...


@dataclass
class Snapshot:
    version: Version
    data: dict[str, Any]


class SnapshotStore(Protocol):
    """Interfae to manage aggregate snapshots at persistence layer"""

    async def load_snapshot(self, key: str, version_number: int) -> Snapshot | None:
        ...

    async def save_snapshot(self, key: str, snap: Snapshot):
        ...

    async def remove_snapshot(self, key: str, version_number: int):
        """Remove a snapshot"""
