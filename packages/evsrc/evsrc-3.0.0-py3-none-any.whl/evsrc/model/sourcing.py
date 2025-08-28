import asyncio
from typing import Callable, Any, TypeVar
from . import (
    EventRecord,
    EventStore,
    Snapshot,
    SnapshotStore,
    Version,
    Aggregate,
    ChangeEvent,
)
from ..time import RealClock, Clock
from weakref import WeakValueDictionary


class EventHandler:
    """Help the hangling of events by aggregates.
    Its use is optional
    """

    def __init__(self, aggregate: Aggregate):
        self._history = []
        self._observers = set()
        self._aggregate = aggregate

    def add_observer(self, callback: Callable[[ChangeEvent, Any], None]):
        """Add callback to be used when a event is trigered, it avoids accidental duplication"""
        if callback in self._observers:
            return

        self._observers.add(callback)
        for event in self._history:
            callback(event, self._aggregate)

    def register_event(self, event: ChangeEvent):
        """Register event to history"""
        self._history.append(event)
        for callback in self._observers:
            callback(event, self._aggregate)


T = TypeVar("T", bound=Aggregate)


class SourcingHandler:
    """Help to construct aggregate stores or repositories to the developer"""

    def __init__(
        self,
        event_store: EventStore,
        snap_store: SnapshotStore | None = None,
        snap_seconds: int = 0,
        clock: Clock | None = None,
    ):
        self._event_store = event_store
        self._snap_store = snap_store
        self._clock = clock or RealClock()
        self._observers = []
        self._aggregates = WeakValueDictionary()
        self._event_records = {}
        self._seconds = snap_seconds

    def add_observer(
        self, callback: Callable[[str, EventRecord], None], pattern: str = ""
    ):
        """Notify about eventchanges to any observer
        Useful for the implementation of projections"""

        self._observers.append(callback)

    async def version_history(self, key: str) -> list[Version]:
        """List all versions of a aggregate."""
        if self._event_store:
            return await self._event_store.list_versions(key)
        if self._snap_store:
            return await self._snap_store.list_versions(key)
        return []

    async def _load_aggregate(
        self, key: str, blank_aggregate: T, records: list[EventRecord]
    ) -> T:
        version_value = records[-1].version.value
        if records[0].version.value != 0:
            if not self._snap_store:
                raise Exception(f"Aggregate {key} has no snaps!")

            snap = await self._snap_store.load_snapshot(key, records[0].version.value)
            if not snap:
                raise Exception(
                    f"Not found Aggregate {key} snap for version {records[0].version.value}"
                )

            blank_aggregate = blank_aggregate.from_dict(snap.data)
            records = records[1:]

        for record in records:
            record.event.apply_on(blank_aggregate)

        print(f"Sending {version_value + 1 }")
        self._link_aggregate(key, blank_aggregate, version_value + 1)
        return blank_aggregate

    async def construct_aggregate(
        self, key: str, blank_aggregate: T, till_ts: int = 0
    ) -> T | None:
        """Construct an aggregate from persistence layer. Default is last version."""

        records = await self._event_store.load_event_records_chunk(key)
        if not records:
            return

        # Automatic snap generation
        if (
            till_ts == 0
            and self._snap_store
            and records[0].version.timestamp
            <= self._clock.timestamp() - self._seconds * 1000
        ):
            await self._event_store.split_chunk(key, records[-1].version.value - 1)
            aggregate = await self._load_aggregate(key, blank_aggregate, records)
            await self._snap_store.save_snapshot(
                key,
                Snapshot(records[-1].version, aggregate.as_dict()),
            )
            return aggregate

        if till_ts != 0:
            while True:
                if records[0].version.timestamp < till_ts:
                    upper = len(records)
                    for idx, record in enumerate(records):
                        if record.version.timestamp > till_ts:
                            upper = idx
                            break

                    records = records[0:upper]
                    break

                records = await self._event_store.load_event_records_chunk(
                    key, records[0].version.value - 1
                )
                if not records:
                    return
        return await self._load_aggregate(key, blank_aggregate, records)

    async def rollback(self, key, timestamp: int):
        if timestamp == 0:
            return

        records = await self._event_store.load_event_records_chunk(key)
        if not records:
            return

        while True:
            if records[0].version.timestamp < timestamp:
                idx = 0
                for idx, record in enumerate(records):
                    if record.version.timestamp > timestamp:
                        await self._event_store.split_chunk(
                            key, records[idx - 1].version.value
                        )
                        await self._event_store.remove_last_event_records_chunk(key)
                return
            else:
                if records[0].version.value != 0 and self._snap_store:
                    await self._snap_store.remove_snapshot(
                        key, records[0].version.value
                    )

                await self._event_store.remove_last_event_records_chunk(key)
                records = await self._event_store.load_event_records_chunk(key)
                if not records:
                    return

    def _link_aggregate(self, key, aggregate, from_version_number):
        next_version = [from_version_number]

        def callback(event: ChangeEvent, _: Aggregate):
            if key not in self._event_records:
                self._event_records[key] = [
                    EventRecord(
                        Version(next_version[0], self._clock.timestamp()), event
                    )
                ]
            else:
                self._event_records[key].append(
                    EventRecord(
                        Version(next_version[0], self._clock.timestamp()), event
                    )
                )
            next_version[0] += 1

        self._clean_destroyed_aggregates()
        aggregate.add_event_observer(callback)
        self._aggregates[key] = aggregate

    def _clean_destroyed_aggregates(self):
        for key in set(self._event_records.keys()) - set(self._aggregates.keys()):
            self._event_records.pop(key)

    async def _notify(self, key):
        await asyncio.gather(
            *[self._notify_to_observer(callback, key) for callback in self._observers]
        )

    async def _notify_to_observer(self, callback, key):
        for record in self._event_records.get(key, []):
            await callback(key, record)

    async def save(self, key: str, aggregate: Aggregate):
        """Store the aggregate"""
        if key not in self._aggregates or self._aggregates[key] != aggregate:
            self._link_aggregate(key, aggregate, 0)

        await self._notify(key)
        records = self._event_records.pop(key, [])
        if records:
            await self._event_store.append_event_records(key, records)
