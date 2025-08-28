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

import base64
from typing import Annotated, Any, Literal

import numpy as np
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    ValidationError,
)
from pydantic.dataclasses import dataclass


def _array_validator(value: Any) -> np.ndarray:
    if isinstance(value, dict):
        shape = [int(s) for s in value["shape"]]
        array = np.frombuffer(base64.b64decode(value["data"]), dtype=value["dtype"]).reshape(shape)
    else:
        array = np.asarray(value, order="C")

    if array.dtype == np.dtypes.ObjectDType:
        raise ValidationError("Invalid array type.")

    return array


def _array_serializer(array: np.ndarray) -> dict[str, Any]:
    return {"data": base64.b64encode(array), "dtype": str(array.dtype), "shape": array.shape}


_SerializableArray = Annotated[
    np.ndarray,
    BeforeValidator(_array_validator),
    PlainSerializer(_array_serializer),
]


@dataclass
class PlotReport:
    text: str
    title: str = "Report"


@dataclass
class Ticks:
    values: list[float]
    labels: list[str]

    def __post_init__(self):
        if len(self.values) != len(self.labels):
            raise ValueError("Ticks values and labels must have the same length.")


class PlotConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    subtitle: str | None = None

    x_label: str
    y_label: str

    x_bounds: tuple[float, float] | None = None
    y_bounds: tuple[float, float] | None = None

    x_ticks: Ticks | None = None
    y_ticks: Ticks | None = None

    axes_ratio: float | None = None
    reverse_yaxis: bool = False

    report: PlotReport | None = None


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PlotData1D:
    x: _SerializableArray
    y: _SerializableArray

    style: Literal["dash", "solid", "scatter"]
    color_index: int | None = None

    x_error: _SerializableArray | None = None
    y_error: _SerializableArray | None = None

    label: str | None = None

    def __post_init__(self):
        if self.x.ndim != 1:
            raise ValueError("x must be 1D.")
        if self.y.ndim != 1:
            raise ValueError("y must be 1D.")
        if len(self.x) != len(self.y):
            raise ValueError("The length of x and y must match.")
        if self.x_error is not None and self.x_error.shape != self.x.shape:
            raise ValueError("The shapes of x and x_error must match.")
        if self.y_error is not None and self.y_error.shape != self.y.shape:
            raise ValueError("The shapes of y and y_error must match.")


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HeatmapData:
    x: _SerializableArray
    y: _SerializableArray
    z: _SerializableArray

    label: str | None = None

    # Whether to display the heatmap values as text.
    heatmap_text: bool = False

    def __post_init__(self):
        if self.x.ndim != 1:
            raise ValueError("x must be 1D.")
        if self.y.ndim != 1:
            raise ValueError("y must be 1D.")
        if self.z.ndim != 2:
            raise ValueError("z must be 2D.")
        if self.z.shape != (len(self.x), len(self.y)):
            raise ValueError("The shape of z must be (len(x), len(y)).")


@dataclass
class Marker:
    x: float
    y: float
    label: str
    color: str
    symbol: Literal["star"]


@dataclass
class VLine:
    value: float
    line_dash: Literal["dash"]
    color: str | None = None


class LinePlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plot_type: Literal["line_plot"] = "line_plot"

    config: PlotConfig
    heatmap: HeatmapData | None = None
    lines: Annotated[list[PlotData1D], Field(min_length=1)]
    markers: list[Marker] = []
    vlines: list[VLine] = []


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class HistogramData:
    data: _SerializableArray
    label: str | None = None
    opacity: float = 0.7
    color_index: int | None = None

    def __post_init__(self):
        if self.data.ndim != 1:
            raise ValueError("data must be 1D.")


class HistogramPlot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plot_type: Literal["histogram"] = "histogram"

    config: PlotConfig
    histograms: list[HistogramData]
    vlines: list[VLine] = []


Plot = LinePlot | HistogramPlot
