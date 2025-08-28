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

import json
import logging
from typing import TYPE_CHECKING

import numpy as np
import qm
from boulderopalscaleupsdk.device.controller.quantum_machines import QuaProgram
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2
from google.protobuf.struct_pb2 import Struct
from pydantic.dataclasses import dataclass
from qm.exceptions import (
    AnotherJobIsRunning,
    CantCalibrateElementError,
)
from qm.jobs.running_qm_job import RunningQmJob

from boulderopalscaleup.controllers import Controller

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from boulderopalscaleup.client import QctrlScaleUpClient


@dataclass
class CalibrationError:
    message: str


class QuantumMachinesController(Controller):
    def __init__(self, qmm: qm.QuantumMachinesManager):
        self.qm: qm.QuantumMachine | None = None
        self.qmm = qmm

    async def run_program(
        self,
        program_request: agent_pb2.RunProgramRequest,
        client: "QctrlScaleUpClient",
    ) -> agent_pb2.RunProgramResponse:
        LOG.info("Running experiment task %s", program_request)

        qua_program = QuaProgram.loads(program_request.program)
        config = qua_program.config.root.model_dump_json(exclude={"qm_version"}, exclude_none=True)

        if program_request.calibrate_elements is not None:
            calibration_response = await self._calibrate_elements(
                elements=list(program_request.calibrate_elements),
                config=config,
                client=client,
            )
            if isinstance(calibration_response, CalibrationError):
                print(f"Calibration skipped: {calibration_response.message}")  # noqa: T201

        self.qm = self._initialize_qm(client, config)

        LOG.info("Executing program.")
        qm_job = self.qm.execute(
            qm.Program(program=qua_program.program, config=qua_program.program.config),
        )  # type: ignore[union-attr]

        LOG.info("Handling results.")
        measurement_data = self._fetch_job_results(qm_job)

        def _convert(array):
            return np.asarray(array).astype(float).tolist()

        raw_data = {k: _convert(v) for k, v in measurement_data.items()}

        raw_data_struct = Struct()
        raw_data_struct.update(raw_data)
        return agent_pb2.RunProgramResponse(raw_data=raw_data_struct)

    async def run_mixer_calibration(
        self,
        calibration_request: agent_pb2.RunQuantumMachinesMixerCalibrationRequest,
        client: "QctrlScaleUpClient",
    ) -> agent_pb2.RunQuantumMachinesMixerCalibrationResponse:
        """
        Run a mixer calibration on the device.
        """
        calibration_response = await self._calibrate_elements(
            list(calibration_request.elements),
            calibration_request.config,
            client,
        )

        match calibration_response:
            case CalibrationError(message=message):
                print(f"Calibration failed: {message}")  # noqa: T201
                return agent_pb2.RunQuantumMachinesMixerCalibrationResponse(
                    success=False,
                    error=message,
                )
            case None:
                return agent_pb2.RunQuantumMachinesMixerCalibrationResponse(success=True)

    async def _calibrate_elements(
        self,
        elements: list[str],
        config: str,
        client: "QctrlScaleUpClient",
    ) -> None | CalibrationError:
        LOG.info("Running mixer calibration for elements: %s", elements)

        client_qm = self._initialize_qm(client, config)

        for element in elements:
            LOG.debug("Calibrating element %s", element)
            try:
                client_qm.calibrate_element(element)
            except CantCalibrateElementError as error:
                return CalibrationError(f"Failed to calibrate element {element}: {error}")
            except AnotherJobIsRunning:
                return CalibrationError(
                    f"Failed to calibrate element {element}: another controller job is running.",
                )

        return None

    def _initialize_qm(self, client: "QctrlScaleUpClient", config_json: str) -> qm.QuantumMachine:  # noqa: ARG002
        """
        Initialize a Quantum Machine from a config JSON string and export the config.
        """
        LOG.info("Initializing QM.")
        qua_config = json.loads(config_json)
        return self.qmm.open_qm(qua_config)  # type: ignore[return-value]

    def _fetch_job_results(self, job: RunningQmJob):
        def _format(data):
            if type(data) is np.ndarray and type(data[0]) is np.void and len(data.dtype) == 1:
                data = data["value"]
            return data

        result_handles = job.result_handles
        result_handles.wait_for_all_values()

        results = {}
        for data in list(result_handles.keys()):
            if hasattr(result_handles, data):
                results[data] = _format(result_handles.get(data).fetch_all())  # type: ignore[union-attr]

        return results
