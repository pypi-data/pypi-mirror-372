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
import abc
from typing import TYPE_CHECKING

from boulderopalscaleupsdk.protobuf.v1 import agent_pb2

if TYPE_CHECKING:
    from boulderopalscaleup.client import QctrlScaleUpClient


class Controller(abc.ABC):
    @abc.abstractmethod
    async def run_program(
        self,
        program_request: agent_pb2.RunProgramRequest,
        client: "QctrlScaleUpClient",
    ) -> agent_pb2.RunProgramResponse:
        raise NotImplementedError

    @abc.abstractmethod
    async def run_mixer_calibration(
        self,
        calibration_request: agent_pb2.RunQuantumMachinesMixerCalibrationRequest,
        client: "QctrlScaleUpClient",
    ) -> agent_pb2.RunQuantumMachinesMixerCalibrationResponse:
        raise NotImplementedError
