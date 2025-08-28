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

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Experiment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    _experiment_name: str

    @property
    def experiment_name(self) -> str:
        return self._experiment_name


class _RangeIterable(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LinspaceIterable(_RangeIterable):
    """A linear space of float values."""

    dtype: Literal["linspace"] = "linspace"

    # The starting value.
    start: float
    # The final value.
    stop: float
    # The number of values. Defaults to 101.
    count: int = Field(default=101)


class RangeIterable(_RangeIterable):
    """A range of values with a specified step."""

    dtype: Literal["range"] = "range"

    # The starting value.
    start: float
    # The final value.
    stop: float
    # The step between values.
    step: float


class LogspaceIterable(_RangeIterable):
    """A range of values spaced evenly on a log scale."""

    dtype: Literal["logspace"] = "logspace"

    # The starting value.
    start: float
    # The final value.
    stop: float
    # The number of values. Defaults to 101.
    count: int = Field(default=101)
    # Base of the logarithm
    base: int = Field(default=10)


class CWSIterable(_RangeIterable):
    """A range of linearly spaced values in center ± width/2."""

    dtype: Literal["cws"] = "cws"

    # The central value. Defaults to the expected value.
    center: float | None
    # The range width.
    width: float
    # The step between values.
    step: float


class HypIterable(_RangeIterable):
    """
    A hyperbolic iterable of values in center ± width/2,
    with points more concentrated around the center.
    """

    dtype: Literal["hyp"] = "hyp"

    # The central value. Defaults to the expected value.
    center: float | None
    # The range width.
    width: float
    # The number of values. Defaults to 51.
    count: int = Field(default=51)
