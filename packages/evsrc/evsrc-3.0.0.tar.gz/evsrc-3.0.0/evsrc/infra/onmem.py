"""Give to developer clients a quick on memory implementation for testing purpose
Don't mock, use this Fake Implementations for your tests"""

from typing import Type
from ..model import (
    EventStore,
    SnapshotStore,
    Version,
    Snapshot,
    EventRecord,
    ConcurrenceError,
)


class OnmemEventStore(EventStore):
    """Implementation of EventStore on memory for testing purpose"""

    def __init__(self):
        self._chunks = {}

    async def list_versions(self, key: str) -> list[Version]:
        versions = []
        for chunk in self._chunks[key]:
            versions.extend([record.version for record in chunk])
        return versions

    async def load_event_records_chunk(
        self, key: str, chunk_version_number: int | None = None
    ) -> list[EventRecord]:
        if key not in self._chunks:
            return []

        if chunk_version_number is None:
            return self._chunks[key][-1]

        for chunk in self._chunks[key]:
            if chunk[-1].version.value == chunk_version_number:
                return chunk

        return []

    async def append_event_records(self, key: str, event_records: list[EventRecord]):
        if key not in self._chunks:
            self._chunks[key] = [[]]

        last_chunk = self._chunks[key][-1]
        if (
            last_chunk
            and last_chunk[-1].version.value + 1 != event_records[0].version.value
        ):
            raise ConcurrenceError(f'Aggregate "{key}" has not continous version')

        last_chunk.extend(event_records)

    async def split_chunk(self, key: str, chunk_version_number: int):
        new_chunks = []
        chunks = self._chunks.pop(key, [])
        for chunk in chunks:
            if (
                chunk
                and chunk[0].version.value <= chunk_version_number
                and chunk[-1].version.value > chunk_version_number
            ):
                new_chunk = [
                    record
                    for record in chunk
                    if record.version.value <= chunk_version_number
                ]

                if new_chunk:
                    new_chunks.append(new_chunk)

                new_chunk = [
                    record
                    for record in chunk
                    if record.version.value > chunk_version_number
                ]
                if new_chunk:
                    new_chunks.append(new_chunk)
                continue

            new_chunks.append(chunk)

        self._chunks[key] = new_chunks

    async def remove_last_event_records_chunk(self, key: str):
        if key in self._chunks and self._chunks[key][-1]:
            self._chunks[key].pop(-1)
            if not self._chunks[key]:
                self._chunks[key].append([])


class OnmemSnapshotStore(SnapshotStore):
    """Implementatioin of SnapshotStore on memory for testing purpose"""

    def __init__(self):
        self._data = {}

    async def list_versions(self, key: str) -> list[Version]:
        if key not in self._data:
            return []
        return [snap.version for snap in self._data[key]]

    async def load_snapshot(
        self, key: str, version_number: int | None = None
    ) -> Snapshot | None:
        if key not in self._data:
            return

        if version_number is None:
            return self._data[key][-1]

        for snap in self._data[key]:
            if snap.version.value == version_number:
                return snap

    async def save_snapshot(self, key: str, snap: Snapshot):
        if key not in self._data:
            self._data[key] = []

        if self._data[key] and (
            self._data[key][-1].version.value >= snap.version.value
            or self._data[key][-1].version.timestamp > snap.version.timestamp
        ):
            raise ConcurrenceError(f'Snapshot for "{key}" is previous to the stored')
        self._data[key].append(snap)

    async def remove_snapshot(self, key: str, version_number: int):
        if key not in self._data:
            return

        self._data[key] = [
            snap for snap in self._data[key] if snap.version.value != version_number
        ]
