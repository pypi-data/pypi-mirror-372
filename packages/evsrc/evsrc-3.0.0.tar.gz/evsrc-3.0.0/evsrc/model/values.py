"""Map Value Objects to dictionaries and construct Value Objects from Dictionaries"""

import abc
from dataclasses import MISSING, dataclass, fields
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Self, get_args, get_origin


@dataclass(frozen=True)
class Value(abc.ABC):
    """Map dataclass objects to primitive dictionaries and construct them"""

    def as_dict(
        self, enum_to_value: bool = True, exclude_defaults: bool = True
    ) -> dict[str, Any]:
        """Convert a Value object to a jsonable dict"""
        result = {}
        for field in fields(self):
            value_ = getattr(self, field.name)
            if (
                not exclude_defaults
                or value_ != field.default
                or (
                    field.default_factory is not MISSING
                    and value_ != field.default_factory()
                )
            ):
                result[field.name] = self._parse_value(
                    value_, enum_to_value, exclude_defaults
                )
        return result

    def _parse_value(self, value, enum_to_value: bool, exclude_defaults: bool):
        if isinstance(value, Value):
            return value.as_dict(enum_to_value, exclude_defaults)
        if isinstance(value, Enum):
            return value.value if enum_to_value else value.name
        if isinstance(value, list):
            return [
                self._parse_value(item, enum_to_value, exclude_defaults)
                for item in value
            ]
        if isinstance(value, tuple):
            return tuple(
                [
                    self._parse_value(item, enum_to_value, exclude_defaults)
                    for item in value
                ]
            )
        if isinstance(value, dict):
            return {
                key: self._parse_value(value_, enum_to_value, exclude_defaults)
                for key, value_ in value.items()
            }
        return value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Construct a Value object from a primitive dict"""
        init_values = {}
        for field in fields(cls):
            if field.name in data:
                init_values[field.name] = cls._construct_value(
                    field.type, data[field.name]
                )
            else:
                if field.default is not MISSING:
                    init_values[field.name] = field.default
                elif field.default_factory is not MISSING:  # Handle default_factory
                    init_values[field.name] = field.default_factory()
                else:
                    raise ValueError(
                        f"Field {field.name} is missing and has no default value."
                    )

        return cls(**init_values)

    @classmethod
    def _construct_value(cls, value_typing, value):
        origin = get_origin(value_typing)
        if origin is None:  # It is a class
            if issubclass(value_typing, Value):
                return value_typing.from_dict(value)
            elif issubclass(value_typing, Enum):
                return (
                    value_typing[value] if type(value) is str else value_typing(value)
                )

        args = get_args(value_typing)
        if origin is list:
            return [cls._construct_value(args[0], item) for item in value]

        if origin is tuple:
            if len(args) == 2 and args[1] == ...:
                return tuple([cls._construct_value(args[0], item) for item in value])
            else:
                return tuple(
                    [
                        cls._construct_value(_typing, item)
                        for _typing, item in zip(args, value)
                    ]
                )
        if origin is dict and args[1] != Any:
            return {
                key: cls._construct_value(args[1], value_)
                for key, value_ in value.items()
            }

        if origin is UnionType:
            if len(args) == 2 and args[1] is NoneType:
                return cls._construct_value(args[0], value)

        return value
