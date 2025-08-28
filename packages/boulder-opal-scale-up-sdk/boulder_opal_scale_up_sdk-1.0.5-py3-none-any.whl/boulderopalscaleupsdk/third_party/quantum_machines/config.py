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

"""Qua Configuration.

Root model & managing qua versions
----------------------------------
A `QuaConfig` Pydantic RootModel definition should be the singular entrypoint for
parsing and validating Qua configuration dictionaries. This will use Pydantic's
discriminated union feature to automatically resolve the correct configuration version
as a function of the `version` string field.

See: https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions

Adding a new version
--------------------
To add a new configuration version:

1. If `_BaseQuaConfig` has fields NOT present in your new version, then update
   `_BaseQuaConfig` to ensure it only contains common fields across all versions.
   Correspondingly, update all existing subclasses of `_BaseQuaConfig` to explicitly
   declare the removed field.

2. Subclass `_BaseQuaConfig` to create your new version.

    * The class name should be `_QuaConfig<VersionTagSlug>`
    * The class must have a PrivateAttr field `_qm_version_spec: str` that follows PyPA
      version specifiers (see references).

Note: the overridden fields will need to use `# type: ignore[assignment]` as MyPy will
    complain about mismatched types from the base class.

Type conventions
----------------
On using Generics for standard collections defined in `typing` module...

    * As of Python 3.9 / PEP 585, the standard collection now implement generics,
      removing the necessity of a parallel type hierarchy in the `typing` modules.
      See: https://peps.python.org/pep-0585
    * qm-qua still uses the alternative type hierarchy for its typing; however since we
      do not intend to support Python <=3.9, this is not necessary for us.
    * Hence, we will override their typing with the standard collection
      (e.g. `Dict` -> `dict`).

On `typing.Mapping` vs `dict`...

    * qm-qua 1.2.1 changes `typing.Dict` typing to `typing.Mapping` typing, the latter
      being a more abstract/generic type that (only) defines the `__getitem__`,
      `__len__`, and `__iter__` magic methods. Further, `typing.Mapping` is covariant
      whilst `dict` is invariant.
    * We should preference `typing.MutableMapping` wherever possible, since we want to
      the broad support of `typing.Mapping`, but need to mutate the config as we build
      programs.
    * A type alias is added here `Mapping = typing.MutableMapping`

References
----------
For field enumeration:

    * In `qm-qua` module: `qm.type_hinting.config_types`
    * Configuration API: https://docs.quantum-machines.co/1.2.1/assets/qua_config.html

For validation details:

    * In `qm-qua` module: `qm.program._qua_config_schema`
    * In `qm-qua` module: `qm.program._qua_config_to_pb`

For information about PyPA's version specifiers:

    * https://packaging.python.org/en/latest/specifications/version-specifiers/#id5
"""

# TODO: Migrate more validations from qm-qua.

# ruff: noqa: UP007, N815, E741
from collections.abc import MutableMapping
from typing import Annotated, Any, Literal, Self, TypeVar, Union

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pydantic import (
    BaseModel,
    BeforeValidator,
    Discriminator,
    Field,
    PrivateAttr,
    RootModel,
    Tag,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

Mapping = MutableMapping
Number = Union[int, float]

T = TypeVar("T", bound=BaseModel)


class Constants(BaseSettings):
    # TODO: Revise how we propagate defaults
    #       We don't want to manage environments and environment overrides, esp since
    #       this will limit our deployment strategy. Consider a approach where default
    #       values are added to the requests schema, and enriched for all inbound
    #       requests as a function of customer. Roughly, something like this:
    #       Controller(customer) --> connect_to_processor(**customer_defaults) --> ...

    model_config = SettingsConfigDict(
        env_prefix="QCSU_QM_QUA_",
    )
    octave_n_rf_out: int = 5
    octave_default_lo_freq: float = 4e9


CONST = Constants()


StandardPort = tuple[str, int, int]
PortReferenceType = Union[tuple[str, int], StandardPort]


class AnalogOutputFilterConfigType(BaseModel):
    feedforward: list[float] = []
    feedback: list[float] = []


def ensure_int(value: Any) -> Any:
    match value:
        case int():
            return value
        case str():
            return int(value)
        case _:
            raise ValueError("Field must be convertible to int.")


IntLike = Annotated[int, BeforeValidator(ensure_int)]


class AnalogOutputPortConfigType(BaseModel):
    offset: Number | None = None
    filter: AnalogOutputFilterConfigType | None = None
    delay: int | None = None
    crosstalk: Mapping[IntLike, Number] = {}
    shareable: bool | None = None


class AnalogInputPortConfigType(BaseModel):
    offset: Number | None = None
    gain_db: int | None = None
    shareable: bool | None = None
    sampling_rate: float | None = None


class DigitalOutputPortConfigType(BaseModel):
    shareable: bool | None = None
    inverted: bool | None = None
    level: Literal["TTL", "LVTTL"] | None = None


class DigitalInputPortConfigType(BaseModel):
    shareable: bool | None = None
    deadtime: int | None = None
    polarity: Literal["RISING", "FALLING"] | None = None
    threshold: Number | None = None


class AnalogOutputPortConfigTypeOctoDac(BaseModel):
    offset: Number | None = None
    filter: AnalogOutputFilterConfigType | None = None
    delay: int | None = None
    crosstalk: Mapping[int, Number] = {}
    shareable: bool | None = None
    connectivity: tuple[str, str] | None = None
    sampling_rate: float | None = None
    upsampling_mode: Literal["mw", "pulse"] | None = None
    output_mode: Literal["direct", "amplified"] | None = None


class LfFemConfigType(BaseModel):
    type: Literal["LF"] | None = None
    analog_outputs: Mapping[int | str, AnalogOutputPortConfigTypeOctoDac] = {}
    analog_inputs: Mapping[int | str, AnalogInputPortConfigType] = {}
    digital_outputs: Mapping[int | str, DigitalOutputPortConfigType] = {}
    digital_inputs: Mapping[int | str, DigitalInputPortConfigType] = {}


Band = Literal[1, 2, 3]


class MwFemAnalogInputPortConfigType(BaseModel):
    sampling_rate: float | None = None
    gain_db: int | None = None
    shareable: bool | None = None
    band: Band | None = None
    downconverter_frequency: float | None = None


class MwUpconverterConfigType(BaseModel):
    frequency: float | None = None


class MwFemAnalogOutputPortConfigType(BaseModel):
    sampling_rate: float | None = None
    full_scale_power_dbm: int | None = None
    band: Band | None = None
    delay: int | None = None
    shareable: bool | None = None
    upconverters: Mapping[IntLike, MwUpconverterConfigType] = {}
    upconverter_frequency: float | None = None


class MwFemConfigType(BaseModel):
    type: Literal["MW"] | None = None
    analog_outputs: Mapping[int | str, MwFemAnalogOutputPortConfigType] = {}
    analog_inputs: Mapping[int | str, MwFemAnalogInputPortConfigType] = {}
    digital_outputs: Mapping[int | str, DigitalOutputPortConfigType] = {}
    digital_inputs: Mapping[int | str, DigitalInputPortConfigType] = {}


class ControllerConfigType(BaseModel):
    type: Literal["opx", "opx1"] | None = None
    analog_outputs: Mapping[int | str, AnalogOutputPortConfigType] = {}
    analog_inputs: Mapping[int | str, AnalogInputPortConfigType] = {}
    digital_outputs: Mapping[int | str, DigitalOutputPortConfigType] = {}
    digital_inputs: Mapping[int | str, DigitalInputPortConfigType] = {}


class OctaveRFOutputConfigType(BaseModel):
    LO_frequency: float = Field(default=CONST.octave_default_lo_freq, ge=2e9, le=18e9)
    LO_source: Literal["internal", "external"] = "internal"
    output_mode: Literal[
        "always_on",
        "always_off",
        "triggered",
        "triggered_reversed",
    ] = "always_off"
    gain: int | float = Field(default=0, ge=-20, le=20, multiple_of=0.5)
    input_attenuators: Literal["ON", "OFF"] = "OFF"
    I_connection: PortReferenceType | None = None
    Q_connection: PortReferenceType | None = None


_RF_SOURCES = Literal[
    "RF_in",
    "loopback_1",
    "loopback_2",
    "loopback_3",
    "loopback_4",
    "loopback_5",
]


class OctaveRFInputConfigType(BaseModel):
    RF_source: _RF_SOURCES | None = None
    LO_frequency: float | None = None
    LO_source: Literal["internal", "external", "analyzer"] | None = None
    IF_mode_I: Literal["direct", "mixer", "envelope", "off"] | None = None
    IF_mode_Q: Literal["direct", "mixer", "envelope", "off"] | None = None


class OctaveSingleIfOutputConfigType(BaseModel):
    port: PortReferenceType | None = None
    name: str | None = None


class OctaveIfOutputsConfigType(BaseModel):
    IF_out1: OctaveSingleIfOutputConfigType | None = None
    IF_out2: OctaveSingleIfOutputConfigType | None = None


FEM_IDX = Literal[1, 2, 3, 4, 5, 6, 7, 8, "1", "2", "3", "4", "5", "6", "7", "8"]


class OPX1000ControllerConfigType(BaseModel):
    type: Literal["opx1000"] | None = None
    fems: Mapping[FEM_IDX, LfFemConfigType | MwFemConfigType] = {}


LoopbackType = tuple[
    tuple[str, Literal["Synth1", "Synth2", "Synth3", "Synth4", "Synth5"]],
    Literal["Dmd1LO", "Dmd2LO", "LO1", "LO2", "LO3", "LO4", "LO5"],
]


class OctaveConfig(BaseModel):
    """Octave configuration for qm-qua 1.1.7."""

    RF_outputs: Mapping[IntLike, OctaveRFOutputConfigType] = {}
    """
    RF Outputs in Octave's up-converter chain.
    OPX/AnalogOutput -> Octave/IFInput -> Octave/RFOutput -> Fridge.
    """

    RF_inputs: Mapping[IntLike, OctaveRFInputConfigType] = {}
    """RF Inputs in Octave's down-converter chain. See IF_Outputs."""

    IF_outputs: OctaveIfOutputsConfigType | None = None
    """
    IF Outputs in Octave's down-converter chain.
    Fridge -> Octave/RFInput -> Octave/IFOutput -> OPX/AnalogInput
    """

    loopbacks: list[LoopbackType] = []
    """
    Loopbacks connected to Octave.
    Each loopback is ((octave_name, octave_port), target_port).
    """

    connectivity: str | None = None
    """
    Default connectivity to OPX (either in host, or host,FEM_IDX format).
    This cannot be set when RF_outputs I/Q connections are set.
    """

    @model_validator(mode="after")
    def validate_connectivity(self) -> Self:
        if self.connectivity is not None:
            for output_num, output in self.RF_outputs.items():
                if output.I_connection or output.Q_connection:
                    raise ValueError(
                        "Octave has ambiguous connectivity: "
                        f"both connectivity set and RF outputs set for {output_num}.",
                    )
        return self

    @model_validator(mode="after")
    def validate_external_lo(self) -> Self:
        rf_2 = self.RF_outputs.get(2)
        rf_3 = self.RF_outputs.get(3)
        if (rf_2 is not None and rf_3 is not None) and (
            rf_3.LO_source == "external" and rf_2.LO_source == "internal"
        ):
            raise ValueError(
                "When utilizing both up-converters 2 and 3 from different sources, converter 2 "
                "must use the external source.",
            )

        rf_4 = self.RF_outputs.get(4)
        rf_5 = self.RF_outputs.get(5)
        if (rf_4 is not None and rf_5 is not None) and (
            rf_5.LO_source == "external" and rf_4.LO_source == "internal"
        ):
            raise ValueError(
                "When utilizing both up-converters 4 and 5 from different sources, converter 4 "
                "must use the external source.",
            )
        return self


class OctaveConfig121(OctaveConfig):
    """Octave configuration for qm-qua 1.2.1."""

    connectivity: Union[str, tuple[str, int]] | None = None  # type: ignore[assignment]


class DigitalInputConfigType(BaseModel):
    delay: int | None = None
    buffer: int | None = None
    port: PortReferenceType | None = None


class IntegrationWeightConfigType(BaseModel):
    cosine: list[tuple[float, int]] | list[float] = []
    sine: list[tuple[float, int]] | list[float] = []


class ConstantWaveFormConfigType(BaseModel):
    type: Literal["constant"] | None = None
    sample: float | None = None


class CompressedWaveFormConfigType(BaseModel):
    type: str | None = None
    samples: list[float] = []
    sample_rate: float | None = None


class ArbitraryWaveFormConfigType(BaseModel):
    type: Literal["arbitrary"] | None = None
    samples: list[float] = []
    max_allowed_error: float | None = None
    sampling_rate: Number | None = None
    is_overridable: bool | None = None


class DigitalWaveformConfigType(BaseModel):
    samples: list[tuple[int, int]] = []


class MixerConfigType(BaseModel):
    intermediate_frequency: float | None = None
    lo_frequency: float | None = None
    correction: tuple[Number, Number, Number, Number] | None = None


class PulseConfigType(BaseModel):
    operation: Literal["measurement", "control"] | None = None
    length: int | None = None
    waveforms: Mapping[str, str] = {}
    digital_marker: str | None = None
    integration_weights: Mapping[str, str] = {}


class SingleInputConfigType(BaseModel):
    port: PortReferenceType | None = None


class MwInputConfigType(BaseModel):
    port: PortReferenceType | None = None
    upconverter: int | None = None


class MwOutputConfigType(BaseModel):
    port: PortReferenceType | None = None


class HoldOffsetConfigType(BaseModel):
    duration: int | None = None


class StickyConfigType(BaseModel):
    analog: bool | None = None
    digital: bool | None = None
    duration: int | None = None


class MixInputConfigType(BaseModel):
    I: PortReferenceType | None = None
    Q: PortReferenceType | None = None
    mixer: str | None = None
    lo_frequency: float | None = None


class InputCollectionConfigType(BaseModel):
    inputs: Mapping[str, PortReferenceType] = {}


class OscillatorConfigType(BaseModel):
    intermediate_frequency: float | None = None
    mixer: str | None = None
    lo_frequency: float | None = None


class OutputPulseParameterConfigType(BaseModel):
    signalThreshold: int | None = None
    signalPolarity: Literal["ABOVE", "ASCENDING", "BELOW", "DESCENDING"] | None = None
    derivativeThreshold: int | None = None
    derivativePolarity: Literal["ABOVE", "ASCENDING", "BELOW", "DESCENDING"] | None = None


class ElementConfig(BaseModel):
    """ElementConfigType for qm-qua 1.1.7."""

    intermediate_frequency: float | None = None
    oscillator: str | None = None
    measurement_qe: str | None = None
    operations: Mapping[str, str] = {}
    singleInput: SingleInputConfigType | None = None
    mixInputs: MixInputConfigType | None = None
    singleInputCollection: InputCollectionConfigType | None = None
    multipleInputs: InputCollectionConfigType | None = None
    time_of_flight: int | None = None
    smearing: int | None = None
    outputs: Mapping[str, PortReferenceType] = {}
    digitalInputs: Mapping[str, DigitalInputConfigType] | None = None
    digitalOutputs: Mapping[str, PortReferenceType] | None = None
    outputPulseParameters: OutputPulseParameterConfigType | None = None
    hold_offset: HoldOffsetConfigType | None = None
    sticky: StickyConfigType | None = None
    thread: str | None = None
    RF_inputs: Mapping[str, tuple[str, int]] | None = None
    RF_outputs: Mapping[str, tuple[str, int]] | None = None

    @model_validator(mode="after")
    def validator_oscillators(self) -> Self:
        if self.intermediate_frequency and self.oscillator:
            raise ValueError(
                "Intermediate frequency and oscillator cannot be defined together.",
            )
        return self


class ElementConfig121(ElementConfig):
    """ElementConfig for qm-qua 1.2.1."""

    MWInput: MwInputConfigType | None = None
    MWOutput: MwOutputConfigType | None = None

    @model_validator(mode="after")
    def validate_outputs(self) -> Self:
        if self.RF_outputs:
            if self.smearing is None:
                raise ValueError("Element with output must have smearing defined.")
            if self.time_of_flight is None:
                raise ValueError(
                    "Element with output must have time_of_flight defined.",
                )
        else:
            if self.smearing:
                raise ValueError("smearing only for elements with outputs.")
            if self.time_of_flight:
                raise ValueError("time_of_flight only for elements with outputs.")

        return self


class _BaseQuaConfig(BaseModel):
    """
    Base Qua configuration.

    Based off 1.1.7; newer versions should shadow fields that need updating.
    """

    _qm_version_spec: str
    """The version specification that this model support.
    Uses PyPA version specifiers."""

    qm_version: str
    """The qm-qua package version used."""

    version: str = "1"
    """The configuration version. This is a field used in Qua's configuration API."""

    oscillators: Mapping[str, OscillatorConfigType] = {}
    """The oscillators used to drive the elements."""

    elements: Mapping[str, ElementConfig] = {}
    """Elements represents a controllable entity wired to a port on the controller."""

    controllers: Mapping[str, ControllerConfigType | OPX1000ControllerConfigType] = {}
    """The controllers."""

    octaves: Mapping[str, OctaveConfig] = {}
    """Any octaves in the stack."""

    integration_weights: Mapping[str, IntegrationWeightConfigType] = {}
    """The integration weight vectors used in the integration and demodulation of data
    returning from a element."""

    waveforms: Mapping[
        str,
        ArbitraryWaveFormConfigType | ConstantWaveFormConfigType | CompressedWaveFormConfigType,
    ] = {}
    """The analog waveforms sent to an element when a pulse is played."""

    digital_waveforms: Mapping[str, DigitalWaveformConfigType] = {}
    """The digital waveforms sent to an element when a pulse is played."""

    pulses: Mapping[str, PulseConfigType] = {}
    """The pulses to be played to the elements."""

    mixers: Mapping[str, list[MixerConfigType]] = {}
    """The IQ mixer calibration properties, used to post-shape the pulse to compensate
    for imperfections in the mixers used for up-converting the analog waveforms."""

    @field_validator("qm_version")
    @classmethod
    def validate_qm_version(cls, vs: str):
        if Version(vs) not in SpecifierSet(cls._qm_version_spec.default):  # type: ignore[attr-defined]
            raise ValueError(f"qm-qua version {vs} not supported.")
        return vs


class _QuaConfig117(_BaseQuaConfig):
    _qm_version_spec: str = PrivateAttr("~=1.1.7")


class _QuaConfig121(_BaseQuaConfig):
    _qm_version_spec: str = PrivateAttr("~=1.2.1")
    elements: Mapping[str, ElementConfig121] = {}  # type: ignore[assignment]
    octaves: Mapping[str, OctaveConfig121] = {}  # type: ignore[assignment]


SUPPORTED_VERSION_SPECS: dict[str, SpecifierSet] = {
    # Nb. the `attr-defined` mypy flag is because Pydantic converts private attributes
    # into pydantic.fields.ModelPrivateAttr, and the value is set in the default.
    cls._qm_version_spec.default: SpecifierSet(cls._qm_version_spec.default)  # type: ignore[attr-defined]
    for cls in _BaseQuaConfig.__subclasses__()
}


def _get_version(data: dict | BaseModel):
    """
    Resolve the correct version Tag from the configuration data.

    Configuration data version will be
    """
    version_str = (
        data.qm_version if isinstance(data, BaseModel) else data.get("qm_version")  # type: ignore[attr-defined]
    )
    if not version_str:
        raise AttributeError("No version specified.")

    version = Version(version_str)

    for spec_name, spec in SUPPORTED_VERSION_SPECS.items():
        if version in spec:
            return spec_name

    raise ValueError(f"Version {version_str} not supported.")


class QuaConfig(RootModel):
    root: Annotated[
        Annotated[_QuaConfig117, Tag("~=1.1.7")] | Annotated[_QuaConfig121, Tag("~=1.2.1")],
        Discriminator(_get_version),
    ]
