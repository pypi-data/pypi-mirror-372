# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from __future__ import annotations

import enum
from typing import overload

__all__ = [
    "Duration",
    "Self",
    "TimeUnit",
]

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Annotated, Any, Literal, Self

import numpy as np
from dateutil.parser import isoparse
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer, TypeAdapter
from pydantic.dataclasses import dataclass

GrpcMetadata = list[tuple[str, str | bytes]]

JobId = str


class BaseType: ...


class FrequencyUnit(str, enum.Enum):
    Hz = "Hz"


@dataclass
class Frequency:
    value: float
    unit: FrequencyUnit  # No default to guarantee clarity of units

    @classmethod
    def from_float_hz(cls, value: float) -> Self:
        return cls(value, FrequencyUnit.Hz)

    def to_int_hz(self) -> int:
        return int(self.to_float_hz())

    def to_float_hz(self) -> float:
        match self.unit:
            case FrequencyUnit.Hz:
                return self.value

    def __gt__(self, other: Frequency) -> bool:
        return self.to_float_hz() > other.to_float_hz()

    def __ge__(self, other: Frequency) -> bool:
        return self.to_float_hz() >= other.to_float_hz()

    def __lt__(self, other: Frequency) -> bool:
        return self.to_float_hz() < other.to_float_hz()

    def __le__(self, other: Frequency) -> bool:
        return self.to_float_hz() <= other.to_float_hz()

    def __sub__(self, rhs: Frequency) -> Frequency:
        if self.unit == rhs.unit:
            return Frequency(self.value - rhs.value, self.unit)
        raise NotImplementedError

    def __add__(self, rhs: Frequency) -> Frequency:
        if self.unit == rhs.unit:
            return Frequency(self.value + rhs.value, self.unit)
        raise NotImplementedError

    def __abs__(self) -> Frequency:
        return Frequency(abs(self.value), self.unit)

    def __str__(self):
        return f"{self.value} {self.unit.value}"

    @overload  # Division by a scalar: e.g. 4.4 Hz // 2.0 = 2.2 Hz
    def __truediv__(self, rhs: float) -> Frequency: ...

    @overload
    def __truediv__(self, rhs: Frequency) -> float: ...

    def __truediv__(self, rhs: float | Frequency) -> Frequency | float:
        if isinstance(rhs, Frequency):
            return self.to_float_hz() / rhs.to_float_hz()
        return Frequency(self.value / rhs, self.unit)

    @overload  # Floor division by a scalar: e.g. 2.2 Hz // 2.0 = 1 Hz
    def __floordiv__(self, rhs: float) -> Frequency: ...

    @overload
    def __floordiv__(self, rhs: Frequency) -> float: ...

    def __floordiv__(self, rhs: float | Frequency) -> Frequency | float:
        if isinstance(rhs, Frequency):
            return self.to_float_hz() // rhs.to_float_hz()
        return Frequency(self.value // rhs, self.unit)

    def __mul__(self, rhs: float) -> Frequency:
        return Frequency(self.value * rhs, self.unit)

    def __rmul__(self, lhs: float) -> Frequency:
        return self.__mul__(lhs)


class TimeUnit(str, enum.Enum):
    S = "s"
    MS = "ms"
    US = "us"
    NS = "ns"


@dataclass
class InvalidDurationDiv:
    message: str
    data: Duration


@dataclass
class InvalidDurationConversion:
    message: str


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Duration:
    value: int
    unit: TimeUnit
    dtype: Literal["duration"] = "duration"
    _np_rep: np.timedelta64 = Field(init=False, repr=False, exclude=True)

    def __post_init__(self):
        err = TypeError(
            f"value must be an integer, got {self.value}{self.unit}. Choose a different unit to "
            "scale it.",
        )
        dec = Decimal(self.value)
        exponent = dec.as_tuple().exponent
        if not isinstance(exponent, int) or exponent < 0:  # pragma: no cover
            raise err

        self.value = int(self.value)
        try:
            self._np_rep = np.timedelta64(self.value, self.unit)
        except ValueError as e:
            raise err from e

    def __gt__(self, other: Duration) -> bool:
        return bool(self._np_rep > other._np_rep)

    def __ge__(self, other: Duration) -> bool:
        return bool(self._np_rep >= other._np_rep)

    def __lt__(self, other: Duration) -> bool:
        return bool(self._np_rep < other._np_rep)

    def __le__(self, other: Duration) -> bool:
        return bool(self._np_rep <= other._np_rep)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Duration):
            return bool(self._np_rep == other._np_rep)
        return False

    def convert(self, unit: TimeUnit) -> Duration | InvalidDurationConversion:
        val: np.float64 = self._np_rep / np.timedelta64(1, unit)
        if val.is_integer():
            return Duration(int(val), unit)
        return InvalidDurationConversion(
            f"fail to convert to {unit} with {self.value} {self.unit}.",
        )

    def to_ns(self) -> Duration:
        match self.convert(TimeUnit.NS):
            case InvalidDurationConversion():
                raise TypeError(f"Cannot convert {self} to nanoseconds.")
            case converted:
                return converted

    def strict_div(self, other: Duration) -> Duration | InvalidDurationDiv:
        self_ns = self.to_ns()
        other_ns = other.to_ns()
        val = np.double(self_ns.value / other_ns.value)
        if np.isclose(val, 0):
            return Duration(int(val), TimeUnit.NS)
        return InvalidDurationDiv(
            f"{self} is not a multiple of {other}",
            Duration(int(val), TimeUnit.NS),
        )

    @staticmethod
    def from_intlike(val: float, unit: TimeUnit) -> Duration:
        if not np.double(val).is_integer():
            raise ValueError("Failed to create a Duration object. Value must be an integer.")
        return Duration(int(val), unit)

    def to_seconds(self) -> float:
        return float(self._np_rep / np.timedelta64(1, "s"))


def ensure_frequency_hz(value: Any) -> Any:
    match value:
        case Frequency():
            return value
        case float() | int():
            return Frequency(value, FrequencyUnit.Hz)
        case dict():
            return TypeAdapter(Frequency).validate_python(value)
        case _:
            raise ValueError("Frequency must be numeric.")


FrequencyHzLike = Annotated[
    Frequency,
    BeforeValidator(ensure_frequency_hz),
    PlainSerializer(lambda x: x.to_float_hz(), return_type=float),
]


def ensure_duration_ns(value: Any) -> Any:
    match value:
        case Duration():
            return value.convert(TimeUnit.NS)
        case float() | int():
            return Duration.from_intlike(value, TimeUnit.NS)
        case dict():
            return TypeAdapter(Duration).validate_python(value)
        case _:
            raise ValueError("Duration must be numeric.")


DurationNsLike = Annotated[Duration, BeforeValidator(ensure_duration_ns)]


@dataclass
class ISO8601Datetime:
    value: datetime

    def __post_init__(self):
        self.value = _validate_iso_datetime(self.value)

    def __str__(self):
        return _serialize_datetime(self.value)

    def strftime(self, fmt: str) -> str:
        """
        Format the datetime value using the given format string.

        Parameters
        ----------
        fmt : str
            The format string to use for formatting.

        Returns
        -------
        str
            The formatted datetime string.
        """
        return self.value.strftime(fmt)


def _validate_iso_datetime(value: Any) -> datetime:
    def _raise_invalid_timezone_error():
        raise ValueError("Datetime must be in UTC timezone.")

    if isinstance(value, ISO8601Datetime):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) != timedelta(0):
            _raise_invalid_timezone_error()
        else:
            return value
    if isinstance(value, str):
        try:
            parsed_datetime = isoparse(value)
            if parsed_datetime.tzinfo is None or parsed_datetime.tzinfo.utcoffset(
                parsed_datetime,
            ) != timedelta(0):
                _raise_invalid_timezone_error()
            else:
                return parsed_datetime
        except Exception as e:
            raise ValueError("Invalid ISO8601 datetime string.") from e
    raise ValueError(
        "Value must be a datetime object, an ISO8601Datetime instance, or a valid ISO8601 string.",
    )


def _serialize_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) != timedelta(0):
        raise ValueError("Datetime must be in UTC timezone.")
    return value.isoformat()


ISO8601DatetimeUTCLike = Annotated[
    datetime,
    BeforeValidator(_validate_iso_datetime),
    PlainSerializer(_serialize_datetime),
]


class JobHistorySortOrder(enum.Enum):
    CREATED_AT_DESC = 1
    CREATED_AT_ASC = 2


class JobSummary(BaseModel):
    id: str
    name: str
    device_name: str
    session_id: str
    created_at: ISO8601DatetimeUTCLike

    def __str__(self):
        return f'JobSummary(name="{self.name}", id="{self.id}")'


class JobDataEntry(BaseModel):
    message: str
    created_at: ISO8601DatetimeUTCLike
    dt: str
    elapsed_time: str

    class Config:
        extra = "allow"


class JobData(BaseModel):
    id: str
    name: str
    session_id: str
    created_at: ISO8601DatetimeUTCLike
    device_name: str
    data: list[JobDataEntry]


DEFAULT_JOB_HISTORY_PAGE = 1
DEFAULT_JOB_HISTORY_PAGE_SIZE = 10
DEFAULT_JOB_HISTORY_SORT_ORDER = JobHistorySortOrder.CREATED_AT_DESC
