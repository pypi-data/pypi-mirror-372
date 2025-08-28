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

from collections.abc import Callable
from datetime import UTC, datetime
from types import EllipsisType
from typing import Annotated, Any, Generic, Literal, Self, TypeVar

from pydantic import BeforeValidator, ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass

from boulderopalscaleupsdk.common.dtypes import (
    Duration,
    DurationNsLike,
    Frequency,
    ISO8601DatetimeUTCLike,
)
from boulderopalscaleupsdk.common.typeclasses import Combine, Eq

T = TypeVar("T")
T2 = TypeVar("T2")
CalibrationStatusT = Literal["approximate", "bad", "good", "stale", "unmeasured"]


@dataclass
class CalibrationThresholds:
    good: float
    approximate: float

    def __post_init__(self):
        if self.good <= 0 or self.approximate < self.good:
            raise ValueError(
                f"Invalid thresholds: good: {self.good}, approximate: {self.approximate}",
            )


@dataclass
class ComponentParameter(Generic[T]):
    value: T
    err_minus: T | None = None
    err_plus: T | None = None
    calibration_status: CalibrationStatusT = "unmeasured"
    updated_at: ISO8601DatetimeUTCLike | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_value(
        cls,
        value: Any,
        target_type: type[float | int | Duration],
    ) -> Self:
        """
        Create a ComponentParameter instance from a value, ensuring it matches the target type.

        Parameters
        ----------
        value : Any
            The input value to validate and convert.
        target_type : type
            The expected type of the value (e.g., float, int, Duration).

        Returns
        -------
        ComponentParameter
            A validated ComponentParameter instance.

        Raises
        ------
        ValueError
            If the value does not match the target type.
        """
        match value:
            case value if isinstance(value, cls):
                if not isinstance(value.value, target_type):
                    raise TypeError("Invalid value type.")
                return value
            case _ if target_type in [float, int]:
                return cls(**value)
            case _ if target_type is Duration:
                value_copy = value.copy()
                duration_ns = TypeAdapter(DurationNsLike).validate_python(value_copy.pop("value"))
                return cls(value=duration_ns, **value_copy)  # type: ignore[arg-type]
            case _:
                raise TypeError("Invalid component value type.")

    @staticmethod
    def combine(
        combine_instance: Combine[T],
        eq_instance: Eq[T],
    ) -> "Combine[ComponentParameter[T]]":
        def _combine(
            first: ComponentParameter[T],
            other: ComponentParameter[Any],
        ) -> ComponentParameter[T]:
            _value = combine_instance.combine(first.value, other.value)
            _err_minus = combine_instance.combine_option(
                first.err_minus,
                other.err_minus,
            )
            _err_plus = combine_instance.combine_option(
                first.err_plus,
                other.err_plus,
            )
            _calibration_status = other.calibration_status

            _updated_at: ISO8601DatetimeUTCLike | None
            if (
                not eq_instance.eq(_value, first.value)
                or not eq_instance.eq_option(_err_minus, first.err_minus)
                or not eq_instance.eq_option(_err_plus, first.err_plus)
                or _calibration_status != first.calibration_status
            ):
                _updated_at = datetime.now(tz=UTC)
            else:
                _updated_at = first.updated_at

            return ComponentParameter(
                value=_value,
                err_minus=_err_minus,
                err_plus=_err_plus,
                calibration_status=_calibration_status,
                updated_at=_updated_at,
            )

        return Combine[ComponentParameter[T]].create(_combine)

    def map(self, fn: Callable[[T], T2]) -> "ComponentParameter[T2]":
        return ComponentParameter(
            value=fn(self.value),
            err_minus=fn(self.err_minus) if self.err_minus is not None else None,
            err_plus=fn(self.err_plus) if self.err_plus is not None else None,
            calibration_status=self.calibration_status,
            updated_at=self.updated_at,
        )

    def merge_with(
        self,
        other: "ComponentParameter[T]",
        combine_value: "Combine[T]",
        eq_value: Eq[T],
    ):
        combined = ComponentParameter[T].combine(combine_value, eq_value).combine(self, other)
        self.value = combined.value
        self.err_minus = combined.err_minus
        self.err_plus = combined.err_plus
        self.calibration_status = combined.calibration_status
        self.updated_at = combined.updated_at

    def update(
        self,
        *,
        value: T | EllipsisType = ...,
        err_minus: T | None | EllipsisType = ...,
        err_plus: T | None | EllipsisType = ...,
        calibration_status: CalibrationStatusT | EllipsisType = ...,
    ) -> None:
        if not isinstance(value, EllipsisType):
            self.value = value
        if not isinstance(err_minus, EllipsisType):
            self.err_minus = err_minus
        if not isinstance(err_plus, EllipsisType):
            self.err_plus = err_plus
        if not isinstance(calibration_status, EllipsisType):
            self.calibration_status = calibration_status
        self.updated_at = datetime.now(UTC)

    def simple_update(
        self,
        *,
        value: T | EllipsisType = ...,
        std: T | None | EllipsisType = ...,
        calibration_thresholds: CalibrationThresholds | EllipsisType = ...,
        to_float: Callable[[T], float],
        from_float: Callable[[float], T],
    ) -> None:
        if not isinstance(value, EllipsisType):
            self.value = value
        if not isinstance(std, EllipsisType):
            if std is None:
                self.err_minus = None
                self.err_plus = None
            else:
                self.err_minus = from_float(to_float(std) / 2.0)
                self.err_plus = from_float(to_float(std) / 2.0)
        if (
            not isinstance(calibration_thresholds, EllipsisType)
            and self.err_minus is not None
            and self.err_plus is not None
        ):
            self.calibration_status = _get_calibration_status_from_thresholds(
                value=to_float(self.value),
                confidence_interval=to_float(self.err_plus) + to_float(self.err_minus),
                calibration_thresholds=calibration_thresholds,
            )
        self.updated_at = datetime.now(UTC)


def update_parameter(
    parameter: ComponentParameter[T],
    *,
    value: T | EllipsisType = ...,
    std: T | None | EllipsisType = ...,
    calibration_thresholds: CalibrationThresholds | EllipsisType = ...,
) -> None:
    """
    Update a ComponentParameter.

    Parameters
    ----------
    parameter : ComponentParameter[T]
        The parameter to update.
    value : T | EllipsisType, optional
        The parameter value. If not provided, the value is left unchanged.
    std : T | None | EllipsisType, optional
        The standard deviation to set the parameter errors.
        If None, the errors are cleared.
        If not provided, the error is left unchanged.
    calibration_thresholds : CalibrationThresholds
        The thresholds to update the calibration status.
        If not provided, the status is left unchanged.
        If the parameter errors are not set, the status is left unchanged.
    """

    # Use type of value to determine generic T.
    match parameter.value:
        case float():
            parameter.simple_update(
                value=value,
                std=std,
                calibration_thresholds=calibration_thresholds,
                to_float=float,  # type: ignore[arg-type]
                from_float=float,  # type: ignore[arg-type]
            )
        case Frequency():
            parameter.simple_update(
                value=value,
                std=std,
                calibration_thresholds=calibration_thresholds,
                to_float=Frequency.to_float_hz,  # type: ignore[arg-type]
                from_float=Frequency.from_float_hz,  # type: ignore[arg-type]
            )
        case _:
            raise TypeError(f"Unsupported type in update: {type(parameter.value)}.")


def _get_calibration_status_from_thresholds(
    value: float,
    confidence_interval: float,
    calibration_thresholds: CalibrationThresholds,
) -> CalibrationStatusT:
    relative_uncertainty = abs(confidence_interval / value)

    if relative_uncertainty < calibration_thresholds.good:
        return "good"
    if relative_uncertainty < calibration_thresholds.approximate:
        return "approximate"
    return "bad"


FloatComponentParameter = Annotated[
    ComponentParameter[float],
    BeforeValidator(lambda value: ComponentParameter.from_value(value, float)),
]
