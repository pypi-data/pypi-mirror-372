from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct

from boulderopalscaleupsdk.device.controller import (
    QBLOXControllerInfo,
    QuantumMachinesControllerInfo,
)
from boulderopalscaleupsdk.device.controller.base import (
    Backend,
    ControllerType,
)
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2


class ControllerResolverService:
    """
    Service for resolving controller-related types and backends.
    """

    def resolve_backend_from_controller(
        self,
        controller_type: ControllerType | QBLOXControllerInfo | QuantumMachinesControllerInfo,
    ) -> Backend:
        """
        Resolve the backend based on the controller type.

        Parameters
        ----------
        controller_type : ControllerType | QBLOXControllerInfo | QuantumMachinesControllerInfo
            The type of the controller, either as an enum or a data structure.

        Returns
        -------
        Backend
            The corresponding backend for the controller type.
        """
        match controller_type:
            case QuantumMachinesControllerInfo() | ControllerType.QUANTUM_MACHINES:
                return Backend.QUA
            case QBLOXControllerInfo() | ControllerType.QBLOX:
                return Backend.QBLOX_Q1ASM

    def resolve_controller_type_from_request(
        self,
        program_request: agent_pb2.RunProgramRequest,
    ) -> ControllerType:
        """
        Resolve the controller type from a RunProgramRequest.

        Parameters
        ----------
        program_request : agent_pb2.RunProgramRequest
            The request containing the controller type.

        Returns
        -------
        ControllerType
            The resolved controller type.

        Raises
        ------
        TypeError
            If the controller type is unknown or not set.
        ValueError
            If the controller type in the request is invalid.
        """
        try:
            controller_type = ControllerType(program_request.controller_type)
        except ValueError as err:
            raise TypeError(
                f"Unknown controller type: {program_request.controller_type}",
            ) from err

        return controller_type

    def resolve_controller_info_from_controller_data_struct(
        self,
        data: Struct,
    ) -> QBLOXControllerInfo | QuantumMachinesControllerInfo:
        """
        Resolve the controller info from a Struct data structure.

        Parameters
        ----------
        data : Struct
            The data structure containing the controller information.

        Returns
        -------
        QBLOXControllerInfo | QuantumMachinesControllerInfo
            The resolved controller info type.

        Raises
        ------
        TypeError
            If the controller type is unknown or not set.
        """
        ref = MessageToDict(data).get("controller_type", None)
        controller_type: type[QuantumMachinesControllerInfo | QBLOXControllerInfo]
        match ref:
            case ControllerType.QUANTUM_MACHINES.value:
                controller_type = QuantumMachinesControllerInfo
            case ControllerType.QBLOX.value:
                controller_type = QBLOXControllerInfo
            case None:
                raise TypeError(
                    "Controller type is not set in the response. "
                    "This may indicate that the device does not have a controller set.",
                )
            case _:
                raise TypeError(
                    f"Unknown controller type: {ref}. "
                    "This may indicate that the device does not have a controller set.",
                )
        return controller_type.model_validate(
            MessageToDict(data),
        )
