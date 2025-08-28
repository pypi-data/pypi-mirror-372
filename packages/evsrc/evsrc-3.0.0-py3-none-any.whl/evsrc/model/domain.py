import abc
from dataclasses import dataclass

from typing import Callable, Any, Self, Protocol
from .values import Value


@dataclass(frozen=True)
class ChangeEvent(Value, abc.ABC):
    """Change of the state of an aggregate"""

    @abc.abstractmethod
    def apply_on(self, aggregate: "Aggregate"):
        """Apply event over aggregate"""


class Aggregate(Protocol):
    """Base of all aggregates under event sourcing approach"""

    @property
    def key(self) -> str:
        """Unique key between same type of aggregate"""
        return ""

    def add_event_observer(self, callback: Callable[[ChangeEvent, Self], None]):
        """Add a observer of event changes"""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        """Construct the aggregate, not compulsory to implement"""
        raise NotImplementedError()

    def as_dict(self) -> dict[str, Any]:
        """Create a snap, not compulsory to implement"""
        raise NotImplementedError()
