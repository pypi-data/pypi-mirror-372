from __future__ import annotations

import asyncio
import json
import time
from functools import singledispatch
from typing import Any, Dict, Optional, Union

import strangeworks as sw
from braket.ahs.analog_hamiltonian_simulation import AnalogHamiltonianSimulation
from braket.annealing.problem import Problem
from braket.circuits import Instruction
from braket.circuits.circuit import Circuit, Gate, QubitSet
from braket.circuits.circuit_helpers import validate_circuit_and_shots
from braket.circuits.compiler_directives import StartVerbatimBox
from braket.circuits.gates import PulseGate
from braket.circuits.serialization import (
    IRType,
    OpenQASMSerializationProperties,
    QubitReferenceType,
    SerializableProgram,
)
from braket.device_schema import GateModelParameters
from braket.device_schema.dwave import (
    Dwave2000QDeviceParameters,
    DwaveAdvantageDeviceParameters,
    DwaveDeviceParameters,
)
from braket.device_schema.dwave.dwave_2000Q_device_level_parameters_v1 import (
    Dwave2000QDeviceLevelParameters,
)
from braket.device_schema.dwave.dwave_advantage_device_level_parameters_v1 import (
    DwaveAdvantageDeviceLevelParameters,
)
from braket.device_schema.ionq import IonqDeviceParameters
from braket.device_schema.oqc import OqcDeviceParameters
from braket.device_schema.rigetti import RigettiDeviceParameters
from braket.device_schema.simulators import GateModelSimulatorDeviceParameters
from braket.error_mitigation import ErrorMitigation
from braket.ir.blackbird import Program as BlackbirdProgram
from braket.ir.openqasm import Program as OpenQASMProgram
from braket.pulse.pulse_sequence import PulseSequence
from braket.schema_common import BraketSchemaBase
from braket.task_result import (
    AnalogHamiltonianSimulationTaskResult,
    AnnealingTaskResult,
    GateModelTaskResult,
    PhotonicModelTaskResult,
)
from braket.tasks import (
    AnalogHamiltonianSimulationQuantumTaskResult,
    AnnealingQuantumTaskResult,
    GateModelQuantumTaskResult,
    PhotonicModelQuantumTaskResult,
    QuantumTask,
)
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Job, Status


class StrangeworksQuantumTask(QuantumTask):
    _product_slug = "amazon-braket"

    def __init__(self, job: Job, *args, **kwargs):
        self.job: Job = job

    @property
    def id(self) -> str:
        """The id of the task.

        Returns
        -------
        id: str
            The id of the task. This is the id of the job in Strangeworks.
        """
        return self.job.slug

    def cancel(self) -> None:
        """Cancel the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.

        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        resource = sw.get_resource_for_product(StrangeworksQuantumTask._product_slug)
        cancel_url = f"{resource.proxy_url()}/jobs/{self.job.external_identifier}"
        # todo: strangeworks-python is rest_client an optional thing. i dont think it should be # noqa: E501
        # this is something we should discuss
        sw.client.rest_client.delete(url=cancel_url)

    def state(self) -> str:
        """Get the state of the task.

        Returns
        -------
        state: str
            The state of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if we find are not able to find the status.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        res = sw.execute_get(
            StrangeworksQuantumTask._product_slug,
            f"jobs/{self.job.external_identifier}",
        )
        self.job = StrangeworksQuantumTask._transform_dict_to_job(res)

        if not self.job.remote_status:
            raise StrangeworksError("Job has no status")
        return self.job.remote_status

    def result(self) -> Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]:
        """Get the result of the task.

        Returns
        -------
        result: Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]
            The result of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if the task did not complete successfully.
            Or unable to fetch the results for the task.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )
        while self.job.status not in {
            Status.COMPLETED,
            Status.FAILED,
            Status.CANCELLED,
        }:
            res = sw.execute_get(
                StrangeworksQuantumTask._product_slug,
                f"jobs/{self.job.external_identifier}",
            )
            self.job = StrangeworksQuantumTask._transform_dict_to_job(res)
            time.sleep(2.5)

        if self.job.status != Status.COMPLETED:
            raise StrangeworksError("Job did not complete successfully")
        # sw.jobs will return type errors until it updates their type hints
        # todo: update strangeworks-python job type hints
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=self.job.slug)
        if not jobs:
            raise StrangeworksError("Job not found.")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found.")
        job: Job = jobs[0]
        if not job.files:
            raise StrangeworksError("Job has no files.")
        # for now the strangeworks-python library still returns the Job.files as Files not JobFiles # noqa: E501
        files = list(
            filter(lambda f: f.file_name == "job_results_braket.json", job.files)
        )
        if len(files) != 1:
            raise StrangeworksError("Job has multiple files")

        file = files[0]
        if not file.url:
            raise StrangeworksError("Job file has no url")
        # why does this say it returns a list of files?
        # did it not just download the file?
        # is the contents not some dictionary?
        # todo probably have to update this in strangeworks-python
        contents = sw.download_job_files([file.url])
        if not contents:
            raise StrangeworksError("Unable to download result file.")
        if len(contents) != 1:
            raise StrangeworksError("Unable to download result file.")
        bsh = BraketSchemaBase.parse_raw_schema(json.dumps(contents[0]))

        if (
            bsh.taskMetadata.deviceId
            != "arn:aws:braket:us-east-1::device/qpu/quera/Aquila"
            and bsh.taskMetadata.deviceId
            != "arn:aws:braket:us-east-1::device/qpu/xanadu/Borealis"
        ):
            task_result = GateModelQuantumTaskResult.from_object(bsh)
        else:
            task_result = bsh
        return task_result

    def async_result(self) -> asyncio.Task:
        raise NotImplementedError

    def metadata(self, use_cached_value: bool = False) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def from_strangeworks_slug(id: str) -> StrangeworksQuantumTask:
        """Get a task from a strangeworks id.

        Parameters
        ----------
        id: str
            The strangeworks id of the task.

        Returns
        -------
        task: StrangeworksQuantumTask
            The task.

        Raises
        ------
        StrangeworksError
            If no task is found for the id.
            Or if multiple tasks are found for the id.
        """
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=id)
        if not jobs:
            raise StrangeworksError("No jobs found for slug")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found for slug")
        job = jobs[0]
        return StrangeworksQuantumTask(job)

    @staticmethod
    def create(
        device_arn: str,
        task_specification: Union[
            Circuit,
            Problem,
            OpenQASMProgram,
            BlackbirdProgram,
            PulseSequence,
            AnalogHamiltonianSimulation,
        ],
        shots: int,
        device_parameters: dict[str, Any] | None = None,
        disable_qubit_rewiring: bool = False,
        tags: dict[str, str] | None = None,
        inputs: dict[str, float] | None = None,
        gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence] | None = None,
        quiet: bool = False,
        reservation_arn: str | None = None,
        *args,
        **kwargs,
    ) -> StrangeworksQuantumTask:
        """AwsQuantumTask factory method that serializes a quantum task specification
        (either a quantum circuit or annealing problem), submits it to Amazon Braket,
        and returns back an AwsQuantumTask tracking the execution.

        Args:
            aws_session (AwsSession): AwsSession to connect to AWS with.

            device_arn (str): The ARN of the quantum device.

            task_specification (Union[Circuit, Problem, OpenQASMProgram, BlackbirdProgram, PulseSequence, AnalogHamiltonianSimulation]): # noqa
                The specification of the quantum task to run on device.

            s3_destination_folder (AwsSession.S3DestinationFolder): NamedTuple, with bucket
                for index 0 and key for index 1, that specifies the Amazon S3 bucket and folder
                to store quantum task results in.

            shots (int): The number of times to run the quantum task on the device. If the device is
                a simulator, this implies the state is sampled N times, where N = `shots`.
                `shots=0` is only available on simulators and means that the simulator
                will compute the exact results based on the quantum task specification.

            device_parameters (dict[str, Any] | None): Additional parameters to send to the device.

            disable_qubit_rewiring (bool): Whether to run the circuit with the exact qubits chosen,
                without any rewiring downstream, if this is supported by the device.
                Only applies to digital, gate-based circuits (as opposed to annealing problems).
                If ``True``, no qubit rewiring is allowed; if ``False``, qubit rewiring is allowed.
                Default: False

            tags (dict[str, str] | None): Tags, which are Key-Value pairs to add to this quantum
                task. An example would be:
                `{"state": "washington"}`

            inputs (dict[str, float] | None): Inputs to be passed along with the
                IR. If the IR supports inputs, the inputs will be updated with this value.
                Default: {}.

            gate_definitions (dict[tuple[Gate, QubitSet], PulseSequence] | None): A `dict`
                of user defined gate calibrations. Each calibration is defined for a particular
                `Gate` on a particular `QubitSet` and is represented by a `PulseSequence`.
                Default: None.

            quiet (bool): Sets the verbosity of the logger to low and does not report queue
                position. Default is `False`.

            reservation_arn (str | None): The reservation ARN provided by Braket Direct
                to reserve exclusive usage for the device to run the quantum task on.
                Note: If you are creating tasks in a job that itself was created reservation ARN,
                those tasks do not need to be created with the reservation ARN.
                Default: None.

        Returns:
            AwsQuantumTask: AwsQuantumTask tracking the quantum task execution on the device.

        Note:
            The following arguments are typically defined via clients of Device.
                - `task_specification`
                - `s3_destination_folder`
                - `shots`

        See Also:
            `braket.aws.aws_quantum_simulator.AwsQuantumSimulator.run()`
            `braket.aws.aws_qpu.AwsQpu.run()`
        """  # noqa E501

        create_task_kwargs = _create_common_params(
            device_arn,
            shots if shots is not None else 100,
        )

        if tags is not None:
            create_task_kwargs.update({"tags": tags})
        inputs = inputs or {}
        gate_definitions = gate_definitions or {}

        if reservation_arn:
            create_task_kwargs.update(
                {
                    "associations": [
                        {
                            "arn": reservation_arn,
                            "type": "RESERVATION_TIME_WINDOW_ARN",
                        }
                    ]
                }
            )

        if isinstance(task_specification, Circuit):
            param_names = {param.name for param in task_specification.parameters}
            if unbounded_parameters := param_names - set(inputs.keys()):
                raise ValueError(
                    f"Cannot execute circuit with unbound parameters: {unbounded_parameters}"  # noqa
                )

        create_task_kwargs = _create_internal(
            task_specification,
            create_task_kwargs,
            device_arn,
            device_parameters or {},
            disable_qubit_rewiring,
            inputs,
            gate_definitions=gate_definitions,
            quiet=quiet,
            *args,
            **kwargs,
        )

        res = sw.execute_post(
            StrangeworksQuantumTask._product_slug, create_task_kwargs, endpoint="runjob"
        )
        sw_job = StrangeworksQuantumTask._transform_dict_to_job(res)
        return StrangeworksQuantumTask(sw_job)

    @staticmethod
    def _transform_dict_to_job(d: Dict[str, Any]) -> Job:
        # create a method that transforms the dict into a job
        # first it must convert the json keys from snake_case to camelCase
        # then it must create a job from the dict
        # todo: this is unfortunate. dont like that we need to do this.
        def to_camel_case(snake_str):
            components = snake_str.split("_")
            # We capitalize the first letter of each component except the first one
            # with the 'title' method and join them together.
            return components[0] + "".join(x.title() for x in components[1:])

        remix = {to_camel_case(key): value for key, value in d.items()}
        return Job.from_dict(remix)


@singledispatch
def _create_internal(
    task_specification: Union[Circuit, Problem, BlackbirdProgram],
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: Union[dict, BraketSchemaBase],
    disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    raise TypeError("Invalid task specification type")


@_create_internal.register
def _(
    pulse_sequence: PulseSequence,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    _device_parameters: Union[
        dict, BraketSchemaBase
    ],  # Not currently used for OpenQasmProgram
    _disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    openqasm_program = OpenQASMProgram(
        source=pulse_sequence.to_ir(),
        inputs=inputs or {},
    )

    create_task_kwargs["action"] = openqasm_program.json()

    return create_task_kwargs


@_create_internal.register
def _(
    openqasm_program: OpenQASMProgram,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: Union[dict, BraketSchemaBase],
    _disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    if inputs:
        inputs_copy = (
            openqasm_program.inputs.copy()
            if openqasm_program.inputs is not None
            else {}
        )
        inputs_copy.update(inputs)
        openqasm_program = OpenQASMProgram(
            source=openqasm_program.source,
            inputs=inputs_copy,
        )
    create_task_kwargs["action"] = openqasm_program.json()
    if device_parameters:
        final_device_parameters = (
            _circuit_device_params_from_dict(
                device_parameters,
                device_arn,
                GateModelParameters(qubitCount=0),  # qubitCount unused
            )
            if isinstance(device_parameters, dict)
            else device_parameters
        )
        create_task_kwargs["deviceParameters"] = final_device_parameters.json(
            exclude_none=True
        )

    return create_task_kwargs


@_create_internal.register
def _(
    serializable_program: SerializableProgram,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: Union[dict, BraketSchemaBase],
    _disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: Optional[dict[tuple[Gate, QubitSet], PulseSequence]],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    openqasm_program = OpenQASMProgram(
        source=serializable_program.to_ir(ir_type=IRType.OPENQASM)
    )
    return _create_internal(
        openqasm_program,
        create_task_kwargs,
        device_arn,
        device_parameters,
        _disable_qubit_rewiring,
        inputs,
        gate_definitions,
        *args,
        **kwargs,
    )


@_create_internal.register
def _(
    blackbird_program: BlackbirdProgram,
    create_task_kwargs: dict[str, any],
    device_arn: str,
    _device_parameters: Union[dict, BraketSchemaBase],
    _disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    create_task_kwargs["action"] = blackbird_program.json()
    return create_task_kwargs


@_create_internal.register
def _(
    circuit: Circuit,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: Union[dict, BraketSchemaBase],
    disable_qubit_rewiring: bool,
    inputs: dict[str, float],
    gate_definitions: dict[tuple[Gate, QubitSet], PulseSequence],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    validate_circuit_and_shots(circuit, create_task_kwargs["shots"])
    paradigm_parameters = GateModelParameters(
        qubitCount=circuit.qubit_count, disableQubitRewiring=disable_qubit_rewiring
    )
    final_device_parameters = (
        _circuit_device_params_from_dict(
            device_parameters or {}, device_arn, paradigm_parameters
        )
        if isinstance(device_parameters, dict)
        else device_parameters
    )

    qubit_reference_type = QubitReferenceType.VIRTUAL

    if (
        disable_qubit_rewiring
        or Instruction(StartVerbatimBox()) in circuit.instructions
        or gate_definitions
        or any(
            isinstance(instruction.operator, PulseGate)
            for instruction in circuit.instructions
        )
    ):
        qubit_reference_type = QubitReferenceType.PHYSICAL

    serialization_properties = OpenQASMSerializationProperties(
        qubit_reference_type=qubit_reference_type
    )

    openqasm_program = circuit.to_ir(
        ir_type=IRType.OPENQASM,
        serialization_properties=serialization_properties,
        gate_definitions=gate_definitions,
    )

    if inputs:
        inputs_copy = (
            openqasm_program.inputs.copy()
            if openqasm_program.inputs is not None
            else {}
        )
        inputs_copy.update(inputs)
        openqasm_program = OpenQASMProgram(
            source=openqasm_program.source,
            inputs=inputs_copy,
        )

    create_task_kwargs |= {
        "action": openqasm_program.json(),
        "deviceParameters": final_device_parameters.json(exclude_none=True),
    }
    return create_task_kwargs


@_create_internal.register
def _(
    problem: Problem,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: Union[
        dict,
        DwaveDeviceParameters,
        DwaveAdvantageDeviceParameters,
        Dwave2000QDeviceParameters,
    ],
    _: bool,
    inputs: dict[str, float],
    gate_definitions: Optional[dict[tuple[Gate, QubitSet], PulseSequence]],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    device_params = _create_annealing_device_params(device_parameters, device_arn)
    create_task_kwargs |= {
        "action": problem.to_ir().json(),
        "deviceParameters": device_params.json(exclude_none=True),
    }

    return create_task_kwargs


@_create_internal.register
def _(
    analog_hamiltonian_simulation: AnalogHamiltonianSimulation,
    create_task_kwargs: dict[str, Any],
    device_arn: str,
    device_parameters: dict,
    _: AnalogHamiltonianSimulationTaskResult,
    inputs: dict[str, float],
    gate_definitions: Optional[dict[tuple[Gate, QubitSet], PulseSequence]],
    *args,
    **kwargs,
) -> StrangeworksQuantumTask:
    create_task_kwargs["action"] = analog_hamiltonian_simulation.to_ir().json()
    return create_task_kwargs


def _circuit_device_params_from_dict(
    device_parameters: dict, device_arn: str, paradigm_parameters: GateModelParameters
) -> GateModelSimulatorDeviceParameters:
    if "errorMitigation" in device_parameters:
        error_migitation = device_parameters["errorMitigation"]
        device_parameters["errorMitigation"] = (
            error_migitation.serialize()
            if isinstance(error_migitation, ErrorMitigation)
            else error_migitation
        )
    if "ionq" in device_arn:
        return IonqDeviceParameters(
            paradigmParameters=paradigm_parameters, **device_parameters
        )
    if "rigetti" in device_arn:
        return RigettiDeviceParameters(paradigmParameters=paradigm_parameters)
    if "oqc" in device_arn:
        return OqcDeviceParameters(paradigmParameters=paradigm_parameters)
    return GateModelSimulatorDeviceParameters(paradigmParameters=paradigm_parameters)


def _create_annealing_device_params(
    device_params: dict[str, Any], device_arn: str
) -> Union[DwaveAdvantageDeviceParameters, Dwave2000QDeviceParameters]:
    """Gets Annealing Device Parameters.

    Args:
        device_params (dict[str, Any]): Additional parameters for the device.
        device_arn (str): The ARN of the quantum device.

    Returns:
        Union[DwaveAdvantageDeviceParameters, Dwave2000QDeviceParameters]: The device parameters.  # noqa

    """
    if not isinstance(device_params, dict):
        device_params = device_params.dict()
    # check for device level or provider level parameters
    device_level_parameters = device_params.get(
        "deviceLevelParameters", None
    ) or device_params.get("providerLevelParameters", {})
    # deleting since it may be the old version
    if "braketSchemaHeader" in device_level_parameters:
        del device_level_parameters["braketSchemaHeader"]

    if "Advantage" in device_arn:
        device_level_parameters = DwaveAdvantageDeviceLevelParameters.parse_obj(
            device_level_parameters
        )
        return DwaveAdvantageDeviceParameters(
            deviceLevelParameters=device_level_parameters
        )
    elif "2000Q" in device_arn:
        device_level_parameters = Dwave2000QDeviceLevelParameters.parse_obj(
            device_level_parameters
        )
        return Dwave2000QDeviceParameters(deviceLevelParameters=device_level_parameters)
    else:
        raise Exception(
            f"Amazon Braket could not find a device with ARN: {device_arn}. "
            "To continue, make sure that the value of the device_arn parameter "
            "corresponds to a valid QPU."
        )


def _create_common_params(device_arn: str, shots: int) -> dict[str, Any]:
    return {
        "deviceArn": device_arn,
        # "outputS3Bucket": s3_destination_folder[0],
        # "outputS3KeyPrefix": s3_destination_folder[1],
        "shots": shots,
    }


@singledispatch
def _format_result(
    result: Union[GateModelTaskResult, AnnealingTaskResult, PhotonicModelTaskResult],
) -> Union[
    GateModelQuantumTaskResult,
    AnnealingQuantumTaskResult,
    PhotonicModelQuantumTaskResult,
]:
    raise TypeError("Invalid result specification type")


@_format_result.register
def _(result: GateModelTaskResult) -> GateModelQuantumTaskResult:
    GateModelQuantumTaskResult.cast_result_types(result)
    return GateModelQuantumTaskResult.from_object(result)


@_format_result.register
def _(result: AnnealingTaskResult) -> AnnealingQuantumTaskResult:
    return AnnealingQuantumTaskResult.from_object(result)


@_format_result.register
def _(result: PhotonicModelTaskResult) -> PhotonicModelQuantumTaskResult:
    return PhotonicModelQuantumTaskResult.from_object(result)


@_format_result.register
def _(
    result: AnalogHamiltonianSimulationTaskResult,
) -> AnalogHamiltonianSimulationQuantumTaskResult:
    return AnalogHamiltonianSimulationQuantumTaskResult.from_object(result)
