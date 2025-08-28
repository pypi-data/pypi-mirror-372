import abc
import asyncio
import time
from datetime import datetime


class Clock(abc.ABC):
    """Interface for injecting time dependency"""

    @abc.abstractmethod
    def timestamp(self) -> int:
        """Current timestamp in miliseconds"""

    @abc.abstractmethod
    async def asleep(self, seconds: float):
        """Async sleep during a time"""

    @abc.abstractmethod
    def sleep(self, seconds: float):
        """Syncronous sleep, blocking current thread"""


class RealClock(Clock):
    """Real clock to inject when production environment"""

    def timestamp(self) -> int:
        """Current timestamp since epoch in miliseconds"""
        return int(datetime.now().timestamp() * 1000)

    async def asleep(self, seconds: float):
        """Async sleep during a time"""
        await asyncio.sleep(seconds)

    def sleep(self, seconds: float):
        """Sincronous sleep during a time"""
        time.sleep(seconds)
