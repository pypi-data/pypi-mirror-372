import json
from typing import Protocol, Type
from aiofs import FileLikeSystem
from dataclasses import asdict
from evsrc.model import (
    ConcurrenceError,
    EventStore,
    SnapshotStore,
    Snapshot,
    EventRecord,
    ChangeEvent,
    Version,
)


class EventClassFactory(Protocol):
    def get_event_class(self, name: str) -> Type[ChangeEvent]:
        ...


class JsonEventStore(EventStore):
    """Implement persistence of event records usin json encoding"""

    def __init__(self, fs: FileLikeSystem, fry: EventClassFactory):
        self._fs = fs
        self._fry = fry

    async def list_versions(self, key: str) -> list[Version]:
        version_number = None
        versions = []
        while True:
            async with self._fs.open(self._get_chunk_fn(key, version_number), "r") as f:
                try:
                    content = json.loads((await f.read()).decode())
                    initial_version = content.get("initial_version", 0)
                    versions.extend(
                        [
                            Version(index + initial_version, ts)
                            for index, ts in enumerate(content["timestamps"])
                        ]
                    )

                    if initial_version == 0:
                        return versions

                    version_number = initial_version - 1
                except FileNotFoundError:
                    return versions

    def _get_chunk_fn(self, key: str, chunk_version_number: int | None):
        if chunk_version_number is None:
            return f"{key}/event_chunk.json"
        return f"{key}/event_chunk_{chunk_version_number}.json"

    async def load_event_records_chunk(
        self,
        key: str,
        chunk_version_number: int | None = None,
    ) -> list[EventRecord]:
        async with self._fs.open(
            self._get_chunk_fn(key, chunk_version_number), "r"
        ) as f:
            result = []
            try:
                content = json.loads((await f.read()).decode())
            except FileNotFoundError:
                return []

            version_number = content.get("initial_version", 0) - 1
            for ts, event_data in zip(content["timestamps"], content["events"]):
                version_number += 1

                event_cls = self._fry.get_event_class(
                    f'{key}/{event_data.pop("__event__")}'
                )
                result.append(
                    EventRecord(
                        Version(version_number, ts), event_cls.from_dict(event_data)
                    ),
                )

            return result

    async def append_event_records(self, key: str, event_records: list[EventRecord]):
        async with self._fs.open(self._get_chunk_fn(key, None), "r+") as f:
            try:
                content = json.loads((await f.read()).decode())
            except FileNotFoundError:
                content = {"timestamps": [], "events": [], "initial_version": 0}

            if (
                content.get("initial_version", 0) + len(content["timestamps"])
                != event_records[0].version.value
            ):
                raise ConcurrenceError(f"Events in {key} are not correlative to saved ")

            if "initial_version" not in content:
                content["initial_version"] = event_records[0].version.value

            timestamps = content["timestamps"]
            events = content["events"]
            for record in event_records:
                timestamps.append(record.version.timestamp)
                event_data = record.event.as_dict()
                event_data["__event__"] = record.event.__class__.__name__
                events.append(event_data)

            await f.write(json.dumps(content).encode())

    async def split_chunk(self, key: str, chunk_version_number: int):
        """Split a chunk into two chunks, first with chunk_version_number"""
        version_number = None
        while True:
            if version_number == chunk_version_number:
                return

            async with self._fs.open(
                self._get_chunk_fn(key, version_number), "r+"
            ) as second:
                content = json.loads((await second.read()).decode())
                initial_version = content.get("initial_version", 0)

                pos = chunk_version_number - initial_version
                if pos < 0:
                    version_number = initial_version - 1
                    continue

                if pos > len(content["timestamps"]) - 1:
                    raise ValueError(
                        f"Version number {chunk_version_number} don't exist yet at aggregate {key}"
                    )

                if pos == len(content["timestamps"]) - 1:
                    return

                async with self._fs.open(
                    self._get_chunk_fn(key, chunk_version_number), "w"
                ) as first:
                    first_content = {
                        "initial_version": initial_version,
                        "timestamps": content["timestamps"][: pos + 1],
                        "events": content["events"][: pos + 1],
                    }
                    await first.write(json.dumps(first_content).encode())

                content = {
                    "initial_version": chunk_version_number + 1,
                    "timestamps": content["timestamps"][pos + 1 :],
                    "events": content["events"][pos + 1 :],
                }
                await second.write(json.dumps(content).encode())
                return

    async def remove_last_event_records_chunk(self, key: str):
        """Remove last chunk of event records"""
        async with self._fs.open(self._get_chunk_fn(key, None), "r+") as f:
            try:
                content = json.loads((await f.read()).decode())
            except FileNotFoundError:
                return

            await self._fs.rm(self._get_chunk_fn(key, None))

            initial_version = content.get("initial_version", 0)
            if initial_version == 0:
                return

        async with self._fs.open(self._get_chunk_fn(key, None), "w") as dest:
            async with self._fs.open(
                self._get_chunk_fn(key, initial_version - 1), "r"
            ) as orig:
                await dest.write(await orig.read())


class JsonSnapshotStore(SnapshotStore):
    """Implement persistence of Snapshots using json encoding."""

    def __init__(self, fs: FileLikeSystem, template: str = "{}.json"):
        self._fs = fs
        self._fs.template = template

    def _get_fn(self, key: str, version_number: int) -> str:
        return f"{key}/snap_{version_number}.json"

    async def load_snapshot(self, key: str, version_number: int) -> Snapshot | None:
        """Load snapshot from persistence"""

        async with self._fs.open(self._get_fn(key, version_number), "r") as f:
            try:
                content = json.loads((await f.read()).decode())

            except FileNotFoundError:
                return

            return Snapshot(Version(**content["version"]), content["data"])

    async def save_snapshot(self, key: str, snap: Snapshot):
        """Save snapshot"""
        async with self._fs.open(self._get_fn(key, snap.version.value), "w") as f:
            await f.write(
                json.dumps(
                    {"version": asdict(snap.version), "data": snap.data}
                ).encode()
            )

    async def remove_snapshot(self, key: str, version_number: int):
        await self._fs.rm(self._get_fn(key, version_number))
