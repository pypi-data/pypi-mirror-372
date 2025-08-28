from __future__ import annotations

import enum
import functools
import importlib
import importlib.metadata
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import qblox_instruments as qbxi
from boulderopalscaleupsdk.device.controller import qblox as qbxs
from packaging.version import Version
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from collections.abc import Iterator

    import qcodes.instrument
    from qblox_instruments.qcodes_drivers import module as qbxi_module
    from qblox_instruments.qcodes_drivers import sequencer as qbxi_sequencer

log = logging.getLogger(__name__)

QbxStackType = dict[str, qbxi.Cluster]

# ==================================================================================================
# compat
# ==================================================================================================
qblox_instruments_version = Version(importlib.metadata.version("qblox-instruments"))
if qblox_instruments_version >= Version("0.17.0"):

    def _get_sequencer_acquisition_status(seq: qbxi_sequencer.Sequencer) -> bool:
        # `check_seq_state` MUST be set to False otherwise, this will never return True, see
        # `device_tests.test_qblox.test_resonator_multi`.
        return seq.get_acquisition_status(timeout=0, check_seq_state=False)
else:

    def _get_sequencer_acquisition_status(seq: qbxi_sequencer.Sequencer) -> bool:
        return seq.get_acquisition_status(timeout=0)


# ==================================================================================================
# Instrument management
# ==================================================================================================


@functools.cache
def get_cluster(name: str, host: str, port: int | None = None) -> qbxi.Cluster:
    """
    Utility to get the Qblox cluster with try-catch.

    Parameters
    ----------
    name: str
        The name of the cluster
    host: str
        The address to connect to the cluster to
    port: int | None, optional
        The TCP port to communicate with the Cluster over. Defaults to None to use the default port.

    Returns
    -------
    qblox_instruments.Cluster
        The cluster

    Raises
    ------
    TimeoutError
    """
    try:
        log.debug("Resolving cluster %s from %s", name, host)
        cluster = qbxi.Cluster(name, host, port=port)
    except KeyError:
        log.warning("A cluster with the name '%s' already exists.", name)
        cluster = cast("qbxi.Cluster", qbxi.Cluster._all_instruments[name])
    except TimeoutError:  # pragma: no cover
        log.error("Timed out trying to connect to cluster %s @ %s", name, host)  # noqa: TRY400
        raise

    return cluster


@functools.cache
def get_cluster_modules(cluster: qbxi.Cluster) -> dict[qbxs.ModuleAddr, qbxi_module.Module]:
    """
    Get all connected modules for a QBLOX cluster.

    Parameters
    ----------
    cluster: qblox_instruments.Cluster
        The cluster

    Returns
    -------
    dict[qbxs.ModuleAddr, qblox_instruments.qcodes_drivers.module.Module]
        The connected modules using Q-CTRL addressing for modules as the key.
    """
    cluster_name = cluster.name
    connected_modules = cluster.get_connected_modules()
    return {qbxs.ModuleAddr(cluster_name, slot): mod for slot, mod in connected_modules.items()}


def get_module(stack: QbxStackType, mod_addr: qbxs.ModuleAddr) -> qbxi_module.Module:
    """
    Retrieve a single module from a QBLOX control stack.

    Parameters
    ----------
    stack: dict[str, qblox_instruments.Cluster]
        The control stack
    mod_addr: boulderopalscaleupsdk.device.controller.qblox.ModuleAddr
        The QBLOX module address

    Returns
    -------
    qblox_instruments.qcodes_drivers.module.Module
        The module if it is connected

    Raises
    ------
    ValueError
        - If the module is addressed to a QBLOX cluster not in the control stack
        - If the module is not connected to any QBLOX cluster in the control stack
    """
    cluster = stack.get(mod_addr.cluster)
    if cluster is None:
        msg = f"Stack does not have cluster {mod_addr.cluster}."
        log.error(msg)
        raise ValueError(msg)

    cluster_modules = get_cluster_modules(cluster)
    mod = cluster_modules.get(mod_addr)
    if mod is None:
        msg = f"Module {mod_addr!s} is not connected."
        log.error(msg)
        raise ValueError(msg)
    return mod


def get_module_types(stack: QbxStackType) -> dict[qbxs.ModuleAddr, qbxs.ModuleType]:
    """
    Get all the module types for each connected module in a stack.

    Parameters
    ----------
    stack: dict[str, qblox_instruments.Cluster]
        The control stack

    Returns
    -------
    dict
        The mapping of module addresses to module types
    """
    modules: dict[qbxs.ModuleAddr, qbxs.ModuleType] = {}
    for cluster in stack.values():
        modules |= {
            addr: _get_module_type(mod) for addr, mod in get_cluster_modules(cluster).items()
        }
    return modules


def _get_module_type(module: qbxi_module.Module) -> qbxs.ModuleType:
    if module.is_qcm_type:
        return qbxs.ModuleType.QCM_RF if module.is_rf_type else qbxs.ModuleType.QCM
    if module.is_qrm_type:
        return qbxs.ModuleType.QRM_RF if module.is_rf_type else qbxs.ModuleType.QRM
    is_qdm = getattr(module, "is_qdm_type", False)
    if is_qdm:
        return qbxs.ModuleType.QDM
    is_qtm = getattr(module, "is_qtm_type", False)
    if is_qtm:
        return qbxs.ModuleType.QTM
    is_eom = getattr(module, "is_eom_type", False)
    if is_eom:
        return qbxs.ModuleType.EOM
    is_linq = getattr(module, "is_linq_type", False)
    if is_linq:
        return qbxs.ModuleType.LINQ
    is_qrc = getattr(module, "is_qrc_type", False)
    if is_qrc:
        return qbxs.ModuleType.QRC

    raise NotImplementedError


# ==================================================================================================
# Arming
# ==================================================================================================


def connect_channel(ch: qbxs.ChannelType, module: qbxi_module.Module, seq_num: int) -> None:
    """
    Connect a sequencer to a channel.

    Parameters
    ----------
    ch: boulderopalscaleupsdk.device.controller.qblox.ChannelType
        The channel to connect to
    module: qblox_instruments.qcodes_drivers.module.Module
        The module the sequencer is located on
    seq_num: int
        The sequencer number
    """

    match ch:
        case qbxs.RealChannel():
            _connect_real_channel(ch, module, seq_num)
        case qbxs.ComplexChannel():
            _connect_iq_channel(ch, module, seq_num)


def _connect_real_channel(ch: qbxs.RealChannel, module: qbxi_module.Module, seq_num: int) -> None:
    seq = module.sequencers[seq_num]
    is_rf = module.is_rf_type
    if ch.port.direction == "out":
        f_name = f"connect_out{ch.port.number}"
        arg = "IQ" if is_rf else "I"
        log.debug("seq:%s -> ch:%s: with %s('%s')", seq.name, ch, f_name, arg)
        getattr(seq, f_name)(arg)
    else:
        conn = f"in{ch.port.number}"
        if is_rf:
            log.debug("seq:%s -> ch:%s: connect_acq('%s')", seq.name, ch, conn)
            seq.connect_acq(conn)
        else:
            log.debug("seq:%s -> ch:%s: connect_acq_I('%s')", seq.name, ch, conn)
            seq.connect_acq_I(conn)


def _connect_iq_channel(ch: qbxs.ComplexChannel, module: qbxi_module.Module, seq_num: int) -> None:
    seq = module.sequencers[seq_num]
    if ch.i_port.direction != ch.q_port.direction:
        raise ValueError("IQ ports of a single channel must be in the same direction.")
    direction = ch.i_port.direction
    if direction == "out":
        i_f = f"connect_out{ch.i_port.number}"
        q_f = f"connect_out{ch.q_port.number}"
        log.debug("seq:%s -> ch:%s: %s('I') + %s('Q')", seq.name, ch, i_f, q_f)
        getattr(seq, i_f)("I")
        getattr(seq, q_f)("Q")
    else:
        i_c = f"in{ch.i_port.number}"
        q_c = f"in{ch.q_port.number}"
        log.debug("seq:%s -> ch:%s: connect_acq_I(%s) + connect_acq_Q(%s)", seq.name, ch, i_c, q_c)
        seq.connect_acq_I(i_c)
        seq.connect_acq_Q(q_c)


def configure_instrument(
    instrument: qcodes.instrument.InstrumentBase,
    parameters: dict[str, Any],
) -> None:
    for name, val in parameters.items():
        delegate = instrument.parameters.get(name)
        if delegate is None:
            raise KeyError(f"Instrument {instrument.name} does not have parameter {name}.")
        delegate.set(val)


@dataclass
class ArmedSequencers:
    """
    Intermediate object tracking armed sequencers ready for execution.

    Attributes
    ----------
    sequencers: dict[SequenceAddr, Sequencer]
        The sequencers that are armed and ready for execution. Armed here means that the necessary
        QCoDeS sequencer parameters have been set, the correct connections have been made, the
        sequence program has been uploaded and the `.arm_sequencer()` API has been called.
    acquisitions_to_collect: set[SequenceAddr]
        The set of sequencers for which we need to collect acquisitions from.
    scopes_to_collect: dict[SequenceAddr, list[str]]
        The named scopes to collect for each SequenceAddr.
    """

    sequencers: dict[qbxs.SequencerAddr, qbxi_sequencer.Sequencer]
    acquisitions_to_collect: set[qbxs.SequencerAddr]
    scopes_to_collect: dict[qbxs.SequencerAddr, list[str]]


def arm_sequencers(  # noqa: C901, PLR0912, PLR0915
    prepared_program: qbxs.PreparedProgram,
    stack: QbxStackType,
    reset: bool = False,
) -> ArmedSequencers:
    """
    Arm sequences from a prepared program.

    Parameters
    ----------
    prepared_program: boulderopalscaleupsdk.device.controller.qblox.PreparedProgram
        The program that we wish to execute
    stack: dict[str, qblox_instruments.Cluster]
        The QBLOX control stack to target
    reset: bool, optional
        When set, will reset each cluster in the stack. Defaults to True.

    Returns
    -------
    ArmedSequencers
        A data class describing the armed sequencers ready for execution

    Raises
    ------
    RuntimeError
        If a targeted sequencer is in an invalid state.
    ValueError
        If a sequence program is invalid (e.g. due to a syntax error)
    """
    if reset:
        for cluster_name, cluster in stack.items():
            log.debug("Resetting cluster:%s", cluster_name)
            cluster.reset()

    modules = {addr: get_module(stack, addr) for addr in prepared_program.modules}

    for mod_addr, mod in modules.items():
        log.debug("Disconnecting mod:%s connections and stopping sequencers", mod_addr)
        mod.disconnect_outputs()
        if mod.is_qrm_type:
            mod.disconnect_inputs()
        mod.stop_sequencer()
        mod_prep = prepared_program.modules[mod_addr]
        mod_params = mod_prep.params.model_dump(exclude_unset=True, exclude_none=True)
        for param_key, param_val in mod_params.items():
            log.debug("Configured module %s: %s=%s", mod_addr, param_key, param_val)
        configure_instrument(mod, mod_params)

    sequencers: dict[qbxs.SequencerAddr, qbxi_sequencer.Sequencer] = {}
    acquisitions_to_collect: set[qbxs.SequencerAddr] = set()
    scopes_to_collect: dict[qbxs.SequencerAddr, list[str]] = {}
    for ref, prepared in prepared_program.sequence_programs.items():
        seq_addr = prepared.sequencer_addr
        ch_out = prepared.ch_out
        ch_in = prepared.ch_in
        mod = modules[seq_addr.module]
        seq_prog = prepared.sequence_program

        seq: qbxi_sequencer.Sequencer = cast(
            "qbxi_sequencer.Sequencer",
            mod.sequencers[seq_addr.number],
        )

        # Check status
        status = seq.get_sequencer_status(timeout=0)
        if status.state not in [qbxi.SequencerStates.IDLE, qbxi.SequencerStates.STOPPED]:
            message = f"Sequencer {seq.name} in invalid state: {status.state}."
            log.exception(message)
            # TODO: Consider changing exception class here; a RuntimeError may not be very helpful
            raise RuntimeError(message)

        # Clear status flags so we have a clean state management
        seq.clear_sequencer_flags()

        # Configure
        try:
            data = seq_prog.sequence_data()
            if data is not None:
                seq.sequence(data)
        except RuntimeError as exc:
            # TODO: Improve error reporting to help debug program errors.
            log.exception("Failed to upload prog:%s to seq:%s.", ref, seq_addr)
            raise ValueError(f"Invalid program: {exc!s}.") from exc

        connect_channel(ch_out, mod, seq_addr.number)
        if ch_in:
            connect_channel(ch_in, mod, seq_addr.number)

        seq_params = prepared.sequence_program.params.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        for param_key, param_val in seq_params.items():
            log.debug("Configured sequencer %s: %s=%s", seq.name, param_key, param_val)
        configure_instrument(seq, seq_params)

        if len(seq_prog.acquisitions) > 0:
            if not mod.is_qrm_type:
                log.warning(
                    "Sequence %s on %s has acquisitions but module cannot readout",
                    ref,
                    seq_addr,
                )
            else:
                acquisitions_to_collect.add(seq_addr)
                if seq_prog.acquisition_scopes:
                    scopes_to_collect[seq_addr] = seq_prog.acquisition_scopes

        # Arm
        seq.arm_sequencer()
        log.info(
            "Armed seq:%s for prog:%s targetting ch_out:%s, ch_in:%s",
            seq_addr,
            ref,
            ch_out,
            ch_in,
        )
        if seq_prog.params_only:
            continue
        sequencers[seq_addr] = seq

    return ArmedSequencers(
        sequencers=sequencers,
        acquisitions_to_collect=acquisitions_to_collect,
        scopes_to_collect=scopes_to_collect,
    )


# ==================================================================================================
# Execution
# ==================================================================================================
class ExecState(enum.Enum):
    DONE = enum.auto()
    ERRORED = enum.auto()
    IN_PROGRESS = enum.auto()
    INVALID_STATE = enum.auto()


def _get_acquisitions_status(seq_addr: qbxs.SequencerAddr, seq: qbxi_sequencer.Sequencer) -> bool:
    try:
        return _get_sequencer_acquisition_status(seq)  # see compat
    except TimeoutError:
        log.debug("seq:%s timed out on get_acquisition_status", seq_addr)
        return False
    except NotImplementedError:  # Not a QRM module
        log.warning("seq:%s does not have any acquisitions but was requested to check", seq_addr)
        return False  # TODO: Consider raising an error / returning invalid state here


def _get_exec_state(
    seq_addr: qbxs.SequencerAddr,
    seq: qbxi_sequencer.Sequencer,
    has_acquisitions: bool = False,
) -> ExecState:
    """
    Map a sequencer's state to ExecState.

    Parameters
    ----------
    seq_addr: boulderopalscaleupsdk.device.controller.qblox.SequencerAddr
        The sequencer's address; used for logging
    seq: qblox_instruments.qcodes_drivers.sequencer.Sequencer
        The sequencer QCoDeS driver instance
    has_acquisitions: bool, optional
        When set, this function will check the sequencer's acquisition status.

    Returns
    -------
    ExecState
        The sequencer execution state
    """
    seq_status: qbxi.SequencerStatus = seq.get_sequencer_status(timeout=0)
    log.debug("seq:%s sequencer status %r", seq_addr, seq_status)

    # -------------------------------------------------------------------------
    # The following checks will return if state can be determined, otherwise pass.
    # -------------------------------------------------------------------------
    # Check status
    status = cast("qbxi.SequencerStatuses", seq_status.status)
    match status:
        case qbxi.SequencerStatuses.ERROR:
            log.error("seq:%s exec done with errors: %s", seq_addr, seq_status.err_flags)
            return ExecState.ERRORED
        case qbxi.SequencerStatuses.WARNING:
            log.warning("seq:%s has warnings: %s", seq_addr, seq_status.warn_flags)
            # pass
        case qbxi.SequencerStatuses.OKAY:
            pass

    # ---------------------------------
    # Check state
    state = cast("qbxi.SequencerStates", seq_status.state)
    match state:
        case qbxi.SequencerStates.IDLE | qbxi.SequencerStates.ARMED:
            log.error("seq:%s not armed", seq_addr)
            return ExecState.INVALID_STATE
        case qbxi.SequencerStates.RUNNING:
            return ExecState.IN_PROGRESS
        case qbxi.SequencerStates.Q1_STOPPED | qbxi.SequencerStates.STOPPED:
            pass

    # ---------------------------------
    # Acquisitions
    if not has_acquisitions:
        return ExecState.DONE

    if qbxi.SequencerStatusFlags.DISARMED in seq_status.info_flags:
        # TODO: Need to clarify behaviour. See: https://qctrl.atlassian.net/browse/SCUP-1203
        #       It appears if the sequencer is disarmed then checking the acquisition status will
        #       hang indefinitely; returning DONE will still give valid results.
        log.warning("seq:%s was disarmed", seq_addr)
        return ExecState.DONE

    acquisitions_ready = _get_acquisitions_status(seq_addr, seq)
    return ExecState.DONE if acquisitions_ready else ExecState.IN_PROGRESS


def _poll_and_iter_ready_sequencers(
    armed_sequencers: ArmedSequencers,
    timeout_poll_res: float = 0.5,
    timeout: float = 30,
) -> Iterator[tuple[qbxs.SequencerAddr, qbxi_sequencer.Sequencer]]:
    """
    Poll a set of armed sequencers yielding each time a single sequencer has finished.

    Parameters
    ----------
    armed_sequencers: ArmedSequencers
        The sequencers to poll; these sequencers must be executed before calling this function,
        otherwise a RuntimeError will be raised
    timeout_poll_res: float, optional
        The time (in seconds) to wait before each iteration of polling. Defaults to 0.5 seconds
    timeout: float, optional
        The total time (in seconds) to poll for until raising a TimeoutError. Defaults to 30 seconds

    Yields
    ------
    tuple[
        boulderopalscaleupsdk.device.controller.qblox.SequencerAddr,
        qblox_instruments.qcodes_drivers.sequencer.Sequencer
    ]
        Yields a ready sequencers as they are found to be ready.

    Raises
    ------
    RuntimeError
        If any sequencer in the armed set is in an invalid state or errored during a run
    TimeoutError
        If a timeout is set and the total elapsed time has exceeded that value

    Notes
    -----
    Each poll on each sequencer is a blocking call as there is limited async support for QBLOX.
    """
    t_start = time.time()
    not_ready = list(armed_sequencers.sequencers.keys())

    while True:
        not_ready2 = []
        for seq_addr in not_ready:
            seq = armed_sequencers.sequencers[seq_addr]
            has_acquisitions = seq_addr in armed_sequencers.acquisitions_to_collect
            match _get_exec_state(seq_addr, seq, has_acquisitions):
                case ExecState.DONE:
                    yield seq_addr, seq
                case ExecState.IN_PROGRESS:
                    not_ready2.append(seq_addr)
                case ExecState.ERRORED | ExecState.INVALID_STATE:
                    raise RuntimeError(f"Sequence:{seq_addr} has execution errors.")

        if not not_ready2:
            break
        not_ready = not_ready2

        elapsed = time.time() - t_start
        log.debug("polling sequencers, %.2f seconds elapsed", elapsed)
        if timeout and elapsed >= timeout:
            for seq_addr in not_ready:
                seq = armed_sequencers.sequencers[seq_addr]
                seq.stop_sequencer()
            raise TimeoutError

        time.sleep(timeout_poll_res)


def execute_armed_sequencers(
    armed: ArmedSequencers,
    timeout_poll_res: float = 1,
    timeout: float = 30,
) -> dict[qbxs.SequencerAddr, qbxs.OutputSequencerAcquisitions]:
    """
    Execute against ArmedSequencers.

    Parameters
    ----------
    armed: ArmedSequencers
        The ArmedSequencers to target. see `arm_sequencers`.
    timeout_poll_res: float, optional
        The polling resolution (in seconds); the amount of time to wait between each poll iteration.
    timeout: float, optional
        The time (in seconds) before a TimeoutError should be raised. If set to zero, this will poll
        indefinitely

    Returns
    -------
    dict[qbxs.SequencerAddr, qbxs.OutputSequencerAcquisitions]
        The execution results for each sequencer.

    Raises
    ------
    TimeoutError
        If `timeout` is set, and the polling time exceeds the configured value.
    RuntimeError
        If a sequencer encounters a run-error or enters an invalid state.
    """
    # Run sequencers
    for seq_addr, seq in armed.sequencers.items():
        seq.start_sequencer()
        log.info("started seq:%s", seq_addr)

    output_type_adapter = TypeAdapter(qbxs.OutputSequencerAcquisitions)

    results: dict[qbxs.SequencerAddr, qbxs.OutputSequencerAcquisitions] = {}
    for ready_seq_addr, ready_seq in _poll_and_iter_ready_sequencers(
        armed,
        timeout_poll_res=timeout_poll_res,
        timeout=timeout,
    ):
        try:
            if ready_seq_addr in armed.acquisitions_to_collect:
                for scope in armed.scopes_to_collect.get(ready_seq_addr, []):
                    ready_seq.store_scope_acquisition(scope)
                acquisitions = ready_seq.get_acquisitions()
                ready_seq.delete_acquisition_data(all=True)
                results[ready_seq_addr] = output_type_adapter.validate_python(acquisitions)
        finally:
            ready_seq.stop_sequencer()
            log.info("seq:%s done and stopped", ready_seq_addr)

    return results


def expand_and_label_results(
    prepared_program: qbxs.PreparedProgram,
    results: dict[qbxs.SequencerAddr, qbxs.OutputSequencerAcquisitions],
) -> dict[str, qbxs.OutputAcquisition]:
    """
    Utility function to re-index and expand the results from execution.

    Parameters
    ----------
    prepared_program: PreparedProgram
        The program that defines the sequence_programs and acquisitions of each sequence_program.
    results: dict[qbxs.SequencerAddr, qbxs.OutputSequencerAcquisitions]
        The results from executing against an armed sequencer.

    Returns
    -------
    dict[str, OutputAcquisition]
        The output acquisitions indexed with string keys following the format `<program>_<acq>`,
        where `<program>` corresponds to the program key in `PreparedProgram.sequence_programs` and
        `<acq>` corresponds to the acquisition key in `SequenceProgram.acquisitions`.
    """
    seq_prog_map: dict[qbxs.SequencerAddr, str] = {
        seq_prog.sequencer_addr: name
        for name, seq_prog in prepared_program.sequence_programs.items()
    }
    return {
        f"{seq_prog_map[addr]}_{acq_ref}": acq.acquisition
        for addr, result in results.items()
        for acq_ref, acq in result.items()
    }
