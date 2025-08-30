from __future__ import annotations

import importlib
import json
import urllib.request
from enum import Enum
from typing import Any, Dict, Optional, Union

import strangeworks as sw
from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.annealing.problem import Problem
from braket.aws.aws_quantum_task import AwsQuantumTask
from braket.circuits import Circuit, Gate, QubitSet
from braket.circuits.gate_calibrations import GateCalibrations
from braket.circuits.noise_model import NoiseModel
from braket.device_schema import DeviceCapabilities, GateModelQpuParadigmProperties
from braket.device_schema.dwave import DwaveProviderProperties
from braket.device_schema.pulse.pulse_device_action_properties_v1 import (
    PulseDeviceActionProperties,
)
from braket.devices.device import Device
from braket.ir.blackbird import Program as BlackbirdProgram
from braket.ir.openqasm import Program as OpenQasmProgram
from braket.parametric.free_parameter import FreeParameter
from braket.parametric.free_parameter_expression import _is_float
from braket.pulse import ArbitraryWaveform, Frame, Port, PulseSequence
from braket.pulse.waveforms import _parse_waveform_from_calibration_schema
from braket.schema_common import BraketSchemaBase
from braket.tasks.quantum_task import QuantumTask
from braket.tasks.quantum_task_batch import QuantumTaskBatch
from networkx import DiGraph, complete_graph, from_edgelist
from strangeworks_core.errors.error import StrangeworksError

from strangeworks_braket.job import StrangeworksQuantumJob
from strangeworks_braket.task import StrangeworksQuantumTask


class AwsDeviceType(str, Enum):
    """Possible AWS device types"""

    SIMULATOR = "SIMULATOR"
    QPU = "QPU"


class StrangeworksDevice(Device):
    def __init__(
        self,
        arn: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        slug: Optional[str] = None,
        noise_model: Optional[NoiseModel] = None,
        **kwargs,
    ):
        super().__init__(name, status)
        self._arn = arn
        self.slug = slug
        self._status = status
        self._arn = arn
        self._gate_calibrations = None
        self._properties = None
        self._provider_name = None
        self._poll_interval_seconds = None
        self._type = None
        self._ports = None
        self._frames = None
        if noise_model:
            self._validate_device_noise_model_support(noise_model)
        self._noise_model = noise_model

    def run(
        self,
        task_specification: Union[
            Circuit,
            Problem,
            OpenQasmProgram,
            BlackbirdProgram,
            PulseSequence,
            AnalogHamiltonianSimulation,
        ],
        shots: Optional[int] = None,
        poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        poll_interval_seconds: Optional[float] = None,
        inputs: Optional[dict[str, float]] = None,
        gate_definitions: Optional[dict[tuple[Gate, QubitSet], PulseSequence]] = None,
        reservation_arn: str | None = None,
        tags: list[str] = None,
        *aws_quantum_task_args: Any,
        **aws_quantum_task_kwargs: Any,
    ) -> QuantumTask:
        """Run a task on the device.
        Parameters
        ----------
        task_specification: Union[Circuit, Problem, OpenQasmProgram]
            The task specification.
        shots: Optional[int]
            The number of shots to run the task for. Defaults to 1000.
        Returns
        -------
        task: QuantumTask (StrangeworksQuantumTask)
            The task that was run.
        """

        if self._noise_model:
            task_specification = self._apply_noise_model_to_circuit(task_specification)
        return StrangeworksQuantumTask.create(
            self._arn,
            task_specification,
            shots if shots is not None else self._default_shots,
            poll_timeout_seconds=poll_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds or self._poll_interval_seconds,
            inputs=inputs,
            gate_definitions=gate_definitions,
            reservation_arn=reservation_arn,
            tags=tags,
            *aws_quantum_task_args,
            **aws_quantum_task_kwargs,
        )

    def run_hybrid(
        self,
        filepath: str,
        hyperparameters: Dict[str, Any],
        input_data: Optional[Dict[str, str]] = None,
        *args,
        **kwargs,
    ) -> QuantumTask:
        """Run a task on the device.
        Parameters
        ----------
        filepath: str
            Path to the python file that will be run.
        hyperparameters: Dict[str, Any]
            Dictionary of hyperparameters to pass to the task.
            Must be json serializable.
        input_data: Dict
            The input data for the job.
        Returns
        -------
        Job: QuantumJob (StrangeworksQuantumJob)
            The job that was run.
        """
        return StrangeworksQuantumJob.create_hybrid(
            self._arn, filepath, hyperparameters, input_data=input_data, *args, **kwargs
        )

    @property
    def status(self) -> str:
        if self._status is None:
            dev = self.get_devices(arns=[self._arn])[0]
            self._status = dev.status

        return self._status

    @staticmethod
    def get_devices(
        arns: Optional[list[str]] = None,
        names: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
    ) -> list[StrangeworksDevice]:
        """Get a list of devices.
        Parameters
        ----------
        arns: Optional[list[str]
            Filter by list of device ARNs. Defaults to None.
        names: Optional[list[str]]
            Filter by list of device names. Defaults to None.
        statuses: Optional[list[str]]
            Filter by list of device statuses. Defaults to None.
        Returns
        -------
        devices: list[SwDevice]
            List of devices that match the provided filters.
        """
        backends = sw.backends(product_slugs=["amazon-braket"])
        devices = []
        for backend in backends:
            if arns and backend.remote_backend_id not in arns:
                continue
            if names and backend.name not in names:
                continue
            if statuses and backend.remote_status not in statuses:
                continue

            devices.append(
                StrangeworksDevice(
                    backend.remote_backend_id,
                    backend.name,
                    backend.remote_status,
                    backend.slug,
                )
            )

        return devices

    def run_batch(
        self,
        task_specifications: Circuit | Problem | list[Circuit | Problem],
        shots: int | None,
        max_parallel: int | None,
        inputs: Dict[str, float] | list[Dict[str, float]] | None,
        *args,
        **kwargs,
    ) -> QuantumTaskBatch:
        raise StrangeworksError("currently not implemented/supported")

    def refresh_metadata(self) -> None:
        """Refresh the `AwsDevice` object with the most recent Device metadata."""
        self._populate_properties()

    def _populate_properties(self) -> None:
        payload = {
            "aws_device_arn": self._arn,
        }
        metadata = sw.execute_post(
            StrangeworksQuantumTask._product_slug, payload, endpoint="metadata"
        )
        self._name = metadata.get("deviceName")
        self._status = metadata.get("deviceStatus")
        self._type = AwsDeviceType(metadata.get("deviceType"))
        self._provider_name = metadata.get("providerName")
        self._properties = BraketSchemaBase.parse_raw_schema(
            metadata.get("deviceCapabilities")
        )
        device_poll_interval = self._properties.service.getTaskPollIntervalMillis
        self._poll_interval_seconds = (
            device_poll_interval / 1000.0
            if device_poll_interval
            else AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL
        )
        self._topology_graph = None
        self._frames = None
        self._ports = None

    @property
    def provider_name(self) -> str:
        """str: Return the provider name"""
        return self._provider_name

    @property
    def arn(self) -> str:
        """str: Return the ARN of the device"""
        return self._arn

    @property
    def gate_calibrations(self) -> Optional[GateCalibrations]:
        """Calibration data for a QPU. Calibration data is shown for gates on particular gubits.  # noqa
        If a QPU does not expose these calibrations, None is returned.

        Returns:
            Optional[GateCalibrations]: The calibration object. Returns `None` if the data  # noqa
            is not present.
        """
        ###########################
        # ToDo:
        # Create Gate calibration call
        ###########################
        if not self._gate_calibrations:
            self._gate_calibrations = self.refresh_gate_calibrations()
        return self._gate_calibrations

    @property
    def properties(self) -> DeviceCapabilities:
        """DeviceCapabilities: Return the device properties

        Please see `braket.device_schema` in amazon-braket-schemas-python_

        .. _amazon-braket-schemas-python: https://github.com/aws/amazon-braket-schemas-python  # noqa
        """
        if self._properties is None:
            self._populate_properties()

        return self._properties

    @property
    def topology_graph(self) -> DiGraph:
        """DiGraph: topology of device as a networkx `DiGraph` object.

        Examples:
            >>> import networkx as nx
            >>> device = AwsDevice("arn1")
            >>> nx.draw_kamada_kawai(device.topology_graph, with_labels=True, font_weight="bold")  # noqa

            >>> topology_subgraph = device.topology_graph.subgraph(range(8))
            >>> nx.draw_kamada_kawai(topology_subgraph, with_labels=True, font_weight="bold")  # noqa

            >>> print(device.topology_graph.edges)

        Returns:
            DiGraph: topology of QPU as a networkx `DiGraph` object. `None` if the topology  # noqa
            is not available for the device.
        """
        if not self._topology_graph:
            self._topology_graph = self._construct_topology_graph()
        return self._topology_graph

    def _construct_topology_graph(self) -> DiGraph:
        """Construct topology graph. If no such metadata is available, return `None`.

        Returns:
            DiGraph: topology of QPU as a networkx `DiGraph` object.
        """
        if hasattr(self.properties, "paradigm") and isinstance(
            self.properties.paradigm, GateModelQpuParadigmProperties
        ):
            if self.properties.paradigm.connectivity.fullyConnected:
                return complete_graph(
                    int(self.properties.paradigm.qubitCount), create_using=DiGraph()
                )
            adjacency_lists = self.properties.paradigm.connectivity.connectivityGraph
            edges = []
            for item in adjacency_lists.items():
                i = item[0]
                edges.extend([(int(i), int(j)) for j in item[1]])
            return from_edgelist(edges, create_using=DiGraph())
        elif hasattr(self.properties, "provider") and isinstance(
            self.properties.provider, DwaveProviderProperties
        ):
            edges = self.properties.provider.couplers
            return from_edgelist(edges, create_using=DiGraph())
        else:
            return None

    @property
    def frames(self) -> dict[str, Frame]:
        """Returns a dict mapping frame ids to the frame objects for predefined frames
        for this device.
        """
        self._update_pulse_properties()
        return self._frames or {}

    @property
    def ports(self) -> dict[str, Port]:
        """Returns a dict mapping port ids to the port objects for predefined ports
        for this device.
        """
        self._update_pulse_properties()
        return self._ports or {}

    def _update_pulse_properties(self) -> None:
        if not hasattr(self.properties, "pulse") or not isinstance(
            self.properties.pulse, PulseDeviceActionProperties
        ):
            return
        if self._ports is None:
            self._ports = {}
            port_data = self.properties.pulse.ports
            for port_id, port in port_data.items():
                self._ports[port_id] = Port(
                    port_id=port_id, dt=port.dt, properties=json.loads(port.json())
                )
        if self._frames is None:
            self._frames = {}
            if frame_data := self.properties.pulse.frames:
                for frame_id, frame in frame_data.items():
                    self._frames[frame_id] = Frame(
                        frame_id=frame_id,
                        port=self._ports[frame.portId],
                        frequency=frame.frequency,
                        phase=frame.phase,
                        is_predefined=True,
                        properties=json.loads(frame.json()),
                    )

    def refresh_gate_calibrations(self) -> Optional[GateCalibrations]:
        """Refreshes the gate calibration data upon request.

        If the device does not have calibration data, None is returned.

        Raises:
            URLError: If the URL provided returns a non 2xx response.

        Returns:
            Optional[GateCalibrations]: the calibration data for the device. None
            is returned if the device does not have a gate calibrations URL associated.
        """
        ###########################
        # ToDo:
        # Create Gate calibration call
        ###########################
        if (
            hasattr(self.properties, "pulse")
            and hasattr(self.properties.pulse, "nativeGateCalibrationsRef")
            and self.properties.pulse.nativeGateCalibrationsRef
        ):
            try:
                with urllib.request.urlopen(
                    self.properties.pulse.nativeGateCalibrationsRef.split("?")[0]
                ) as f:
                    json_calibration_data = self._parse_calibration_json(
                        json.loads(f.read().decode("utf-8"))
                    )
                    return GateCalibrations(json_calibration_data)
            except urllib.error.URLError as e:
                raise urllib.error.URLError(
                    f"Unable to reach {self.properties.pulse.nativeGateCalibrationsRef}"
                ) from e
        else:
            return None

    def _parse_waveforms(self, waveforms_json: dict) -> dict:
        waveforms = {}
        for waveform in waveforms_json:
            parsed_waveform = _parse_waveform_from_calibration_schema(
                waveforms_json[waveform]
            )
            waveforms[parsed_waveform.id] = parsed_waveform
        return waveforms

    def _parse_pulse_sequence(
        self, calibration: dict, waveforms: dict[ArbitraryWaveform]
    ) -> PulseSequence:
        return PulseSequence._parse_from_calibration_schema(
            calibration, waveforms, self.frames
        )

    def _parse_calibration_json(
        self, calibration_data: dict
    ) -> dict[tuple[Gate, QubitSet], PulseSequence]:
        """Takes the json string from the device calibration URL and returns a structured dictionary of
        corresponding `dict[tuple[Gate, QubitSet], PulseSequence]` to represent the calibration data.

        Args:
            calibration_data (dict): The data to be parsed. Based on
                https://github.com/aws/amazon-braket-schemas-python/blob/main/src/braket/device_schema/pulse/native_gate_calibrations_v1.py.

        Returns:
            dict[tuple[Gate, QubitSet], PulseSequence]: The
            structured data based on a mapping of `tuple[Gate, Qubit]` to its calibration represented as a
            `PulseSequence`.

        """  # noqa: E501
        waveforms = self._parse_waveforms(calibration_data["waveforms"])
        parsed_calibration_data = {}
        for qubit_node in calibration_data["gates"]:
            qubit = calibration_data["gates"][qubit_node]
            for gate_node in qubit:
                for gate in qubit[gate_node]:
                    gate_capitalized = getattr(
                        self,
                        f"_{self.provider_name.upper()}_GATES_TO_BRAKET",
                        {},
                    ).get(gate_node.capitalize(), gate_node.capitalize())

                    if gate_capitalized == "Iswap":
                        gate_capitalized = "ISwap"
                    elif gate_capitalized == "Cz":
                        gate_capitalized = "CZ"
                    elif gate_capitalized == "Gphase":
                        gate_capitalized = "GPhase"
                    elif gate_capitalized == "Phaseshift":
                        gate_capitalized = "PhaseShift"
                    elif gate_capitalized == "Cnot":
                        gate_capitalized = "CNot"
                    elif gate_capitalized == "Pswap":
                        gate_capitalized = "PSwap"
                    elif gate_capitalized == "Xy":
                        gate_capitalized = "XY"
                    elif gate_capitalized == "Cphaseshift":
                        gate_capitalized = "CPhaseShift"
                    elif gate_capitalized == "Cphaseshift00":
                        gate_capitalized = "CPhaseShift00"
                    elif gate_capitalized == "Cphaseshift01":
                        gate_capitalized = "CPhaseShift01"
                    elif gate_capitalized == "Cphaseshift10":
                        gate_capitalized = "CPhaseShift10"
                    elif gate_capitalized == "Cv":
                        gate_capitalized = "CV"
                    elif gate_capitalized == "Cy":
                        gate_capitalized = "CY"
                    elif gate_capitalized == "Ecr":
                        gate_capitalized = "ECR"
                    elif gate_capitalized == "Xx":
                        gate_capitalized = "XX"
                    elif gate_capitalized == "Yy":
                        gate_capitalized = "YY"
                    elif gate_capitalized == "Zz":
                        gate_capitalized = "ZZ"
                    elif gate_capitalized == "Ccnot":
                        gate_capitalized = "CCNot"
                    elif gate_capitalized == "Cswap":
                        gate_capitalized = "CSwap"
                    elif gate_capitalized == "Gpi":
                        gate_capitalized = "GPi"
                    elif gate_capitalized == "Prx":
                        gate_capitalized = "PRx"
                    elif gate_capitalized == "Gpi2":
                        gate_capitalized = "GPi2"
                    elif gate_capitalized == "Ms":
                        gate_capitalized = "MS"
                    elif gate_capitalized == "Pulsegate":
                        gate_capitalized = "PulseGate"

                    gate_obj = (
                        getattr(
                            importlib.import_module("braket.circuits.gates"),
                            gate_capitalized,
                        )
                        if gate_capitalized is not None
                        else None
                    )
                    qubits = QubitSet([int(x) for x in gate["qubits"]])
                    if gate_obj is None:
                        # We drop out gates that are not implemented in the BDK
                        continue

                    argument = None
                    if gate["arguments"]:
                        argument = (
                            float(gate["arguments"][0])
                            if _is_float(gate["arguments"][0])
                            else FreeParameter(gate["arguments"][0])
                        )
                    gate_qubit_key = (
                        (gate_obj(argument), qubits)
                        if argument
                        else (gate_obj(), qubits)
                    )
                    gate_qubit_pulse = self._parse_pulse_sequence(
                        gate["calibrations"], waveforms
                    )
                    parsed_calibration_data[gate_qubit_key] = gate_qubit_pulse

        return parsed_calibration_data
