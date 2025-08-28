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
"""
Client for the Boulder Opal Scale Up API.
"""

import logging
import os
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING

import grpc
from boulderopalscaleupsdk.agent import Agent, AgentSettings, TaskHandler
from boulderopalscaleupsdk.common.dtypes import (
    DEFAULT_JOB_HISTORY_PAGE,
    DEFAULT_JOB_HISTORY_PAGE_SIZE,
    DEFAULT_JOB_HISTORY_SORT_ORDER,
    JobData,
    JobHistorySortOrder,
    JobId,
    JobSummary,
)
from boulderopalscaleupsdk.device.config_loader import DeviceConfigLoader, DeviceInfo
from boulderopalscaleupsdk.device.controller.resolver import ControllerResolverService
from boulderopalscaleupsdk.device.defcal import DefCalData
from boulderopalscaleupsdk.device.device import DeviceData, DeviceSummary
from boulderopalscaleupsdk.device.processor import (
    SuperconductingProcessor,
)
from boulderopalscaleupsdk.device.processor.superconducting_processor import Resonator, Transmon
from boulderopalscaleupsdk.experiments import Experiment
from boulderopalscaleupsdk.grpc_interceptors.auth import AuthInterceptor
from boulderopalscaleupsdk.plotting import Plot
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2, device_pb2, device_pb2_grpc, task_pb2
from boulderopalscaleupsdk.routines import Routine
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct
from pydantic import TypeAdapter
from rich.console import Console
from rich.table import Table

from boulderopalscaleup.auth import get_default_api_key_auth
from boulderopalscaleup.constants import API_KEY_NAME, SERVER_URL
from boulderopalscaleup.controllers._base import Controller
from boulderopalscaleup.plots import Plotter

from .utils import display_element

if TYPE_CHECKING:
    from boulderopalscaleupsdk.common.dtypes import GrpcMetadata
    from qctrlclient import ApiKeyAuth

LOG = logging.getLogger(__name__)


def _get_package_version() -> str:
    """
    Get the version of this package.

    Returns
    -------
    str
        The package version, or "unknown" if it cannot be determined.
    """
    try:
        return metadata.version("boulder-opal-scale-up")
    except metadata.PackageNotFoundError:
        return "unknown"


class ScaleUpServerError(Exception):
    """
    Exception raised by client based on server behavior.
    """

    def __init__(self, message: str):
        super().__init__(message)


class ScaleUpClientError(Exception):
    """
    Exception raised by client based on user behavior.
    """

    def __init__(self, message: str):
        super().__init__(message)


class QctrlScaleUpClient:
    """
    Q-CTRL Scale Up client providing API access to experiments.
    """

    def __init__(  # noqa: PLR0913
        self,
        controller: Controller,
        app_name: str,
        organization_slug: str,
        api_key: str | None = None,
        local_mode: bool = False,
        api_url: str = SERVER_URL,
    ):
        """
        Initialize the client.

        Parameters
        ----------
        controller : Controller
            The controller instance used to manage QPU-interfacing controllers.
        app_name : str
            The name of the application using the Scale Up API.
        organization_slug : str
            The name of the organization using the Scale Up API.
        api_key : str or None, optional
            The API key for authenticating with the Q-CTRL server. If not provided,
            the key is retrieved from the environment variable `QCTRL_API_KEY`.
        api_url : str, optional
            The URL of the Boulder Opal Scale Up server. Defaults to the value of `SERVER_URL`.
        local_mode : bool, optional
            If True, uses a local unauthenticated server. Defaults to False.

        Raises
        ------
        RuntimeError
            If no API key is provided and the environment variable `QCTRL_API_KEY` is not set.
        """
        self.controller = controller
        self.app_name = app_name
        self.auth: ApiKeyAuth | None
        if local_mode:
            self.auth = None
        else:
            if api_key is None:
                try:
                    api_key = os.environ[API_KEY_NAME]
                except KeyError as error:
                    raise RuntimeError(
                        "No API key provided in environment or function call. "
                        "To call this function without arguments, "
                        f"save your API key's value in the {API_KEY_NAME} "
                        "environment variable.",
                    ) from error
            self.auth = get_default_api_key_auth(api_key)
        self.agent_settings = AgentSettings(agent_id="dummy_agent_id", remote_url=api_url)
        self.request_metadata: GrpcMetadata = [
            ("organization-slug", organization_slug),
            ("client-version", _get_package_version()),
        ]

        self._current_device_name: str | None = None
        self._device_mgr = device_pb2_grpc.DeviceManagerServiceStub(self._create_channel(api_url))
        self._controller_resolver = ControllerResolverService()
        self._silent = False

    @property
    # Read-only to force use of set_current_device which performs checks and is async
    def current_device_name(self) -> str | None:
        return self._current_device_name

    async def create_device(self, device_name: str, device_config: DeviceInfo | Path) -> None:
        """
        Create and initialize a device for experiments.

        Parameters
        ----------
        device_name : str
            The name of the device to be created.
        device_config : DeviceInfo or Path
            The device information, or the file path to the device configuration file.

        Raises
        ------
        ScaleUpServerError
            If the device initialization fails on the server.
        """
        if isinstance(device_config, Path):
            device_config = DeviceConfigLoader(device_config).load_device_info()

        if not self._silent:
            _display_message("Creating device...")

        request = device_pb2.CreateRequest(
            app_name=self.app_name,
            device_name=device_name,
            device_data=dict_to_struct(device_config.to_dict()),
        )
        response: device_pb2.CreateResponse = self._device_mgr.Create(
            request,
            metadata=self.request_metadata,
        )
        if not response.done:
            raise ScaleUpServerError("Failed to create device.")

        if not self._silent:
            _display_message(f"Device '{device_name}' created successfully.")

    async def copy_device(self, from_device_name: str, to_device_name: str) -> None:
        """
        Copy a device to a new device with the specified name.

        Parameters
        ----------
        from_device_name : str
            The name of the device to copy from.
        to_device_name : str
            The name of the new device to create.

        Raises
        ------
        ScaleUpServerError
            If the new device creation on server fails on the server.
        """

        if not self._silent:
            _display_message(f"Copying device '{from_device_name}' to '{to_device_name}'...")

        request = device_pb2.CopyRequest(
            from_device_name=from_device_name,
            to_device_name=to_device_name,
        )
        response: device_pb2.CopyResponse = self._device_mgr.Copy(
            request,
            metadata=self.request_metadata,
        )
        if not response.done:
            raise ScaleUpServerError("Failed to copy device.")

        if not self._silent:
            _display_message(
                f"Device '{from_device_name}' copied to '{to_device_name}' successfully.",
            )

    async def set_current_device(self, device_name: str) -> None:
        """
        Set which device to use in routines and experiments.

        Parameters
        ----------
        device_name : str
            The name of the device to mark as the current device.
        """
        if not self._silent:
            _display_message(f"Setting current device to '{device_name}'...")

        self._silent = True
        # We check device exists by retrieving it
        await self.get_device_data(device_name)
        self._silent = False

        self._current_device_name = device_name
        if not self._silent:
            _display_message(f"Current device set to '{device_name}'.")

    async def get_device_summary(self, device_name: str | None = None) -> DeviceSummary:
        """
        Retrieve the summary of a device.

        Parameters
        ----------
        device_name : str or None, optional
            The device whose summary should be retrieved. Defaults to the current device.

        Returns
        -------
        DeviceSummary
            The summary of the device.

        Raises
        ------
        RuntimeError
            If the device name is not set.
        ScaleUpServerError
            If the response from the server is invalid.
        """
        device_name = self._default_to_current_device(device_name)
        if not self._silent:
            _display_message(f"Generating device summary for device '{device_name}'...")

        request = device_pb2.GetMetadataRequest(device_name=device_name)
        response = self._device_mgr.GetMetadata(request, metadata=self.request_metadata)
        if response is None or not isinstance(response, device_pb2.GetMetadataResponse):
            raise ScaleUpServerError("Failed to retrieve device summary.")

        if not self._silent:
            _display_message(f"Device summary for '{device_name}' generated successfully.")
        return DeviceSummary.model_validate(MessageToDict(response.metadata))

    async def display_device_data_sheet(
        self,
        device_name: str | None = None,
        node_name: str | None = None,
    ) -> None:
        """
        Display a data sheet of the components in the device.

        Parameters
        ----------
        device_name : str or None, optional
            The name of the device to display. Defaults to the current device.
        node_name : str or None, optional
            The name of the node to display. If not provided, all applicable nodes are summarized.
        """
        device_name = self._default_to_current_device(device_name)
        device = await self.get_device_data(device_name)
        if node_name is None:
            display_nodes = {
                key: node
                for key, node in device.qpu.nodes.items()
                if isinstance(node, Resonator | Transmon)
            }
        else:
            node = device.qpu.nodes.get(node_name)
            if not isinstance(node, Resonator | Transmon):
                raise ValueError(f"{node_name} is not a Resonator or Transmon.")
            display_nodes = {node_name: node}
        for name, node in sorted(display_nodes.items()):
            display_element(name, node)

    @staticmethod
    def display(
        data: DeviceSummary | JobSummary | list[DeviceSummary] | list[JobSummary],
    ) -> None:
        data_list = data if isinstance(data, list) else [data]

        if len(data_list) == 0:
            raise ValueError("Data cannot be an empty list.")

        data_type = type(data_list[0])
        if not isinstance(data_list[0], DeviceSummary | JobSummary):
            raise TypeError(
                "Data must be a DeviceSummary, JobSummary, or a list of them. "
                f"Got {data_type.__name__} instead.",
            )

        if not all(isinstance(item, data_type) for item in data_list):
            raise TypeError(
                f"All items in the list must be of the same {data_type.__name__}.",
            )

        title = ""
        match data_list[0]:
            case JobSummary():
                title = "Job summary"
            case DeviceSummary():
                title = "Device summary"

        _data = [element.model_dump() for element in data_list]

        console = Console()
        table = Table(title=title)
        keys = _data[0].keys()
        for key in keys:
            table.add_column(str(key))

        for item in _data:
            row = [str(item[key]) for key in keys]
            table.add_row(*row)

        console.print(table)

    async def get_device_data(
        self,
        device_name: str | None = None,
    ) -> DeviceData:
        """
        Get latest data for a device.

        Parameters
        ----------
        device_name : str or None, optional
            The name of the device. Defaults to the current device.
        """
        device_name = self._default_to_current_device(device_name)

        if not self._silent:
            _display_message(f"Retrieving data for device '{device_name}'...")

        request = device_pb2.GetDataRequest(device_name=device_name)
        response: device_pb2.GetDataResponse = self._device_mgr.GetData(
            request,
            metadata=self.request_metadata,
        )
        if (
            response.processor_data is None
            or response.controller_data is None
            or response.defcals is None
        ):
            raise ScaleUpServerError(f"Failed to retrieve {device_name} device data.")

        if not self._silent:
            _display_message(f"Data for device '{device_name}' retrieved successfully.")

        superconducting_processor = SuperconductingProcessor.from_dict(
            MessageToDict(response.processor_data),
        )
        controller_info = (
            self._controller_resolver.resolve_controller_info_from_controller_data_struct(
                response.controller_data,
            )
        )
        defcals = {}
        for item in response.defcals:
            defcal_data = DefCalData(**MessageToDict(item))
            defcals[(defcal_data.gate, tuple(defcal_data.addr))] = defcal_data

        return DeviceData(
            qpu=superconducting_processor,
            controller_info=controller_info,
            _defcals=defcals,
        )

    async def update_device(self, new_processor_details: SuperconductingProcessor) -> None:
        """
        Update the current device's processor information.

        Parameters
        ----------
        new_processor_details : SuperconductingProcessor
            The new processor information for the current device.

        Raises
        ------
        RuntimeError
            If no current device has been set.
        """
        if self.current_device_name is None:
            raise RuntimeError(
                f"No current device set. Call {self.set_current_device.__name__} first.",
            )

        if not self._silent:
            _display_message(f"Updating device '{self.current_device_name}'...")

        request = device_pb2.UpdateRequest(
            device_name=self.current_device_name,
            processor_data=ParseDict(new_processor_details.to_dict(), Struct()),
        )
        response: device_pb2.UpdateResponse = self._device_mgr.Update(
            request,
            metadata=self.request_metadata,
        )
        if response is None or not isinstance(response, device_pb2.UpdateResponse):
            raise ScaleUpServerError("Invalid response received when updating device.")

        if not self._silent:
            _display_message(f"Device '{self.current_device_name}' updated successfully.")

    async def delete_device(self, device_name: str) -> None:
        """
        Delete the specified device.

        Parameters
        ----------
        device_name : str
            The name of the device to delete.
        """

        if not self._silent:
            _display_message(f"Deleting device '{device_name}'...")
        if not self._delete_device_from_server(device_name):
            raise ScaleUpServerError(f"Failed to delete device '{device_name}' from server.")

        if self.current_device_name == device_name:
            self._current_device_name = None

    async def get_devices(self) -> list[DeviceSummary]:
        """
        Retrieve a summary for all devices.

        Returns
        -------
        list[DeviceSummary]:
            The information about the devices.
        """
        if not self._silent:
            _display_message("Retrieving summary for all devices...")

        request = device_pb2.GetAllDevicesMetadataRequest()
        response = self._device_mgr.GetAllDevicesMetadata(request, metadata=self.request_metadata)
        if response is None or not isinstance(response, device_pb2.GetAllDevicesMetadataResponse):
            raise ScaleUpServerError("Invalid response when attempting to get device summary.")

        if not self._silent:
            _display_message("Summary for all devices retrieved successfully.")

        return [
            DeviceSummary.model_validate(MessageToDict(metadata)) for metadata in response.metadatas
        ]

    def _default_to_current_device(self, device_name: str | None) -> str:
        if isinstance(device_name, str):
            return device_name

        if self.current_device_name is None:
            raise RuntimeError(
                f"No current device has been set. Call {self.set_current_device.__name__} first.",
            )

        return self.current_device_name

    def _delete_device_from_server(self, device_name: str) -> bool:
        request = device_pb2.DeleteRequest(device_name=device_name)
        response = self._device_mgr.Delete(request, metadata=self.request_metadata)
        if response is None or not isinstance(response, device_pb2.DeleteResponse):
            LOG.error("Invalid response from server when attempting to delete device")
            return False
        return response.done

    def _get_channel_interceptors(self) -> list:
        """
        Get the interceptors for the gRPC channel.
        """
        return [AuthInterceptor(self.auth)] if self.auth else []

    def _create_channel(self, api_url: str) -> grpc.Channel:
        """
        Create a gRPC channel.
        """
        options = [
            ("grpc.max_send_message_length", 1024 * 1024 * 50),  # 50MB
            ("grpc.max_receive_message_length", 1024 * 1024 * 50),  # 50MB
        ]
        host = api_url.split(":")[0]
        if host in ["localhost", "127.0.0.1", "0.0.0.0", "::"]:
            channel = grpc.insecure_channel(api_url, options=options)
        else:
            channel = grpc.secure_channel(api_url, grpc.ssl_channel_credentials(), options=options)
        return grpc.intercept_channel(channel, *self._get_channel_interceptors())

    async def run_experiment(self, experiment: Experiment) -> JobId:
        """
        Execute an experiment.

        Parameters
        ----------
        experiment : Experiment
            The experiment object containing the routine and parameters to be executed.

        Returns
        -------
        JobId
            The job ID of the executed experiment.

        Raises
        ------
        RuntimeError
            If the device name is not set before running the experiment.
        """
        if self.current_device_name is None:
            raise RuntimeError(
                f"No current device set. Call {self.set_current_device.__name__} first.",
            )

        self.agent = Agent(
            self.agent_settings,
            AgentTaskHandler(self),
            grpc_interceptors=self._get_channel_interceptors(),
        )

        job_id = await self.agent.start_session(
            app=self.app_name,
            metadata=self.request_metadata,
            device_name=self.current_device_name,
            routine=experiment.experiment_name,
            data=dict_to_struct(experiment.model_dump()),
        )

        if job_id is None:
            raise ScaleUpServerError("Failed to start experiment session.")

        return job_id

    async def run_routine(self, routine: Routine) -> JobId:
        """
        Execute a routine.

        Parameters
        ----------
        routine : Routine
            The routine object containing the procedure and parameters to be executed.

        Returns
        -------
        JobId
            The job ID of the executed routine.

        Raises
        ------
        RuntimeError
            If the current device name is not set before running the routine.
        """
        if self.current_device_name is None:
            raise RuntimeError(
                f"No current device set. Call {self.set_current_device.__name__} first.",
            )

        self.agent = Agent(
            self.agent_settings,
            AgentTaskHandler(self),
            grpc_interceptors=self._get_channel_interceptors(),
        )

        job_id = await self.agent.start_session(
            app=self.app_name,
            metadata=self.request_metadata,
            device_name=self.current_device_name,
            routine=routine.routine_name,
            data=dict_to_struct(routine.model_dump()),
        )

        if job_id is None:
            raise ScaleUpServerError("Failed to start routine session.")

        return job_id

    async def get_job_data(self, job_id: str) -> JobData:
        """
        Retrieves details about a specific job executed on the device, such as
        its status, execution results, and associated metadata.

        Parameters
        ----------
        job_id : str
            The ID of the job to retrieve.

        Returns
        -------
        JobData
            The job data.

        Raises
        ------
        ScaleUpServerError
            If the response is invalid.
        """
        if not self._silent:
            _display_message(f"Retrieving data for job '{job_id}'...")

        response = self._device_mgr.GetJob(
            device_pb2.GetJobRequest(job_id=job_id),
            metadata=self.request_metadata,
        )
        if response is None:
            raise ScaleUpServerError("Invalid response.")
        if not isinstance(response, device_pb2.GetJobResponse):
            raise ScaleUpServerError("Unexpected response type.")

        if not self._silent:
            _display_message(f"Retrieved data for job '{job_id}'.")
        return JobData.model_validate(MessageToDict(response.job_data))

    async def get_jobs(
        self,
        device_name: str | None = None,
        job_name: str | None = None,
        page: int = DEFAULT_JOB_HISTORY_PAGE,
        limit: int = DEFAULT_JOB_HISTORY_PAGE_SIZE,
        sort_order: JobHistorySortOrder = DEFAULT_JOB_HISTORY_SORT_ORDER,
    ) -> list[JobSummary]:
        """
        Retrieves all the jobs that have been previously executed on the given device.

        Parameters
        ----------
        device_name : str
            The name of the device to filter the history by. Defaults to current.
        job_name : str, optional
            The name of the job to filter the history by. Defaults to None.
        page : int, optional
            The page number to retrieve. Defaults to 1.
        limit : int, optional
            The number of jobs to retrieve per page. Defaults to 10.
        sort_order : JobHistorySortOrder, optional
            The sort order for the results.
            Defaults to reverse chronological.

        Returns
        -------
        list[JobSummary]
            The history of jobs run.

        Raises
        ------
        ScaleUpServerError
            If the response is invalid.
        """
        device_name = self._default_to_current_device(device_name)

        if not self._silent:
            _display_message(f"Retrieving jobs for device '{device_name}'...")

        response = self._device_mgr.ListJobs(
            device_pb2.ListJobsRequest(
                device_name=device_name,
                job_name=job_name,
                page=page,
                limit=limit,
                sort_order=sort_order.value,
            ),
            metadata=self.request_metadata,
        )
        if response is None:
            raise ScaleUpServerError("Invalid response.")
        if not isinstance(response, device_pb2.ListJobsResponse):
            raise ScaleUpServerError("Unexpected response type.")

        if not self._silent:
            _display_message(
                f"Retrieved jobs for device '{device_name}'.\nPage {page}/{response.total_pages}.",
            )
        return [JobSummary.model_validate(MessageToDict(job)) for job in response.jobs]

    async def get_job_summary(self, job_id: str) -> JobSummary:
        """
        Retrieves a summary of a specific job executed on the device.

        Parameters
        ----------
        job_id : str
            The ID of the job to retrieve.

        Returns
        -------
        JobSummary
            The job summary.

        Raises
        ------
        ScaleUpServerError
            If the response is invalid.
        """
        if not self._silent:
            _display_message(f"Retrieving summary for job '{job_id}'...")

        response = self._device_mgr.GetJobSummary(
            device_pb2.GetJobSummaryRequest(job_id=job_id),
            metadata=self.request_metadata,
        )
        if response is None:
            raise ScaleUpServerError("Invalid response.")
        if not isinstance(response, device_pb2.GetJobSummaryResponse):
            raise ScaleUpServerError("Unexpected response type.")

        if not self._silent:
            _display_message(f"Retrieved summary for job '{job_id}'.")
        return JobSummary.model_validate(MessageToDict(response.job_summary_data))


class AgentTaskHandler(TaskHandler):
    def __init__(self, client: QctrlScaleUpClient) -> None:
        self._client = client

    async def handle(
        self,
        request: agent_pb2.RunProgramRequest
        | agent_pb2.RunQuantumMachinesMixerCalibrationRequest
        | agent_pb2.DisplayResultsRequest
        | agent_pb2.AskRequest,
    ) -> (
        agent_pb2.RunProgramResponse
        | agent_pb2.RunQuantumMachinesMixerCalibrationResponse
        | agent_pb2.DisplayResultsResponse
        | agent_pb2.AskResponse
        | task_pb2.TaskErrorDetail
    ):
        match request:
            case agent_pb2.RunProgramRequest():
                return await self._client.controller.run_program(request, self._client)
            case agent_pb2.RunQuantumMachinesMixerCalibrationRequest():
                return await self._client.controller.run_mixer_calibration(request, self._client)
            case agent_pb2.DisplayResultsRequest():
                return await _display_results(request)
            case agent_pb2.AskRequest():
                return await _ask_user(request)


@dataclass
class CalibrationError:
    message: str


async def _display_results(
    results: agent_pb2.DisplayResultsRequest,
) -> agent_pb2.DisplayResultsResponse:
    """
    Display results to the user.
    """

    LOG.info("Displaying results")

    if results.plots is not None:
        for plot in results.plots:
            plot_data: Plot = TypeAdapter(Plot).validate_json(plot)
            Plotter(plot_data).figure.show()

    if results.message is not None:
        _display_message(results.message)

    return agent_pb2.DisplayResultsResponse()


async def _handle_yes_no_ask(ask: agent_pb2.AskRequest) -> agent_pb2.AskResponse:
    """
    Handle yes/no questions from the user.
    """
    while True:
        response = input(f"{ask.message}: ").strip().lower()
        if response in ("y", "yes"):
            return agent_pb2.AskResponse(response="y")
        if response in ("n", "no"):
            return agent_pb2.AskResponse(response="n")
        _display_message("Please answer with 'y' or 'n'.")


async def _ask_user(ask: agent_pb2.AskRequest) -> agent_pb2.AskResponse:
    """
    Ask user interactively.
    """
    _display_message(ask.message)
    match ask.expected_response_type:
        case "yes_no":
            return await _handle_yes_no_ask(ask)
        case _:
            raise ScaleUpServerError(
                f"Unknown expected response type '{ask.expected_response_type}'",
            )


def dict_to_struct(dictionary: dict) -> Struct:
    result = Struct()
    result.update(dictionary)
    return result


def _display_message(message: str) -> None:
    console = Console()
    console.is_jupyter = False
    console.print(message)
