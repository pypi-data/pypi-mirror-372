from typing import Protocol, Self


class FileLike(Protocol):
    """Interface to a object with async file behaviour"""

    async def __aenter__(self) -> Self:
        ...

    async def read(self) -> bytes:
        ...

    async def write(self, content: bytes):
        ...

    async def __aexit__(self, ex: Exception):
        ...


class FileLikeSystem(Protocol):
    """Manage FileLike objects in a encapsulated system"""

    @property
    def template(self) -> str:
        ...

    @template.setter
    def template(self, value: str):
        ...

    def open(self, filename: str, mode: str = "r") -> FileLike:
        ...

    async def rm(self, filename: str):
        ...
