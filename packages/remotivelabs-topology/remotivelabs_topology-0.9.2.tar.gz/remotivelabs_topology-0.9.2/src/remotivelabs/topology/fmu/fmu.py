from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, List, Optional, Set, TypedDict

import numpy as np
from fmpy import dump, extract, instantiate_fmu, read_model_description, simulate_fmu

from remotivelabs.broker import RestbusSignalConfig
from remotivelabs.topology.namespaces.can import CanNamespace
from remotivelabs.topology.time.async_ticker import create_ticker

_logger = logging.getLogger(__name__)


class SimulationKwargs(TypedDict):
    filename: str
    model_description: str
    fmu_instance: Any  # fmpy is not available on 3.8
    output_interval: float
    terminate: bool
    fmu_state: Optional[object]
    start_time: float
    input: Any  # numpy is not available on 3.8
    step_finished: Optional[Callable[[float, object], bool]]


class UnsupportedFMUModelError(Exception):
    """Raised when the FMU is incorrectly configured"""


class FMUModel:
    """
    FMU simulation example

    Attribution, Torsten Sommer
    https://stackoverflow.com/questions/75730464/how-to-using-fmpy-extract-the-list-of-continuous-time-states
    """

    def __init__(
        self,
        fmu_filename: Path,
        run_forever: bool,
        input_mapping: dict[str, str] | None,
        output_mapping: dict[str, str] | None,
    ) -> None:
        model_description = read_model_description(fmu_filename)

        if not model_description.coSimulation.canGetAndSetFMUstate:
            raise UnsupportedFMUModelError("The FMU does not support get/set FMU state.")

        self._input = {var.name: 0 for var in model_description.modelVariables if var.causality == "input"}

        unzipdir = extract(fmu_filename)

        fmu_instance = instantiate_fmu(
            unzipdir=unzipdir,
            model_description=model_description,
        )

        if model_description.defaultExperiment is None:
            raise UnsupportedFMUModelError("Missing defaultExperiment")

        self._simulation_kwargs: SimulationKwargs = {
            "filename": unzipdir,
            "model_description": model_description,
            "fmu_instance": fmu_instance,
            "output_interval": float(model_description.defaultExperiment.stepSize),
            "terminate": False,
            "fmu_state": None,
            "start_time": 0.0,
            "input": None,
            "step_finished": None,
        }
        self._fmu_filename = fmu_filename
        self._stop_time = None if run_forever else model_description.defaultExperiment.stopTime
        self._reached_end = False
        self._input_mapping = input_mapping
        self._output_mapping = output_mapping
        self._last_entry: Any = None
        self._read_cache: Any = {}
        self._sub_task: asyncio.Task | None = None
        self._step_event = asyncio.Event()

    def print(self) -> None:
        """Print the model information and variables of an FMU"""
        dump(self._fmu_filename)

    def get_step_size(self) -> float:
        """Get the step size in seconds"""
        return self._simulation_kwargs["output_interval"]

    def reset(self) -> None:
        """Reset the state and time of the FMU

        Notice that inputs are not reset!
        """
        self._simulation_kwargs["fmu_instance"].reset()
        self._simulation_kwargs["fmu_state"] = None
        self._simulation_kwargs["start_time"] = 0.0
        self._reached_end = False

    def update_input(self, updated_input: dict[str, Any]) -> None:
        """Manually update inputs instead of using input_mapping.

        This is useful to handle other inputs than signals.
        """
        if self._input_mapping is not None:
            raise ValueError("Cannot combine update_input with input_mapping")
        self._input = {**self._input, **updated_input}

    async def request(self, args: dict[str, Any], output: Set[str]) -> dict[str, Any]:
        """Simulate a request towards the FMU by:
        1. setting inputs
        2. waiting until next FMU step
        3. returning a subset of the output signals
        """
        self.update_input(args)
        data = await self._wait_next_step()
        if data is None:
            return {}
        keys_to_extract = data.dtype.names if hasattr(data, "dtype") else data
        return {key: data[key] for key in output if key in keys_to_extract}

    async def _wait_next_step(self) -> Any:
        """Wait until the next step is performed"""
        await self._step_event.wait()
        return self._last_entry

    async def _notify_next_step(self) -> None:
        # trigger event
        self._step_event.set()
        # yield to anyone waiting for the event
        await asyncio.sleep(0)
        # clear event to force others to wait for next trigger
        self._step_event.clear()

    def _make_input(self) -> Any:
        def dict_to_nparray(f: dict):
            if not f:
                return None
            field_names = [(key, np.array([value]).dtype) for key, value in f.items()]
            return np.array([tuple(f.values())], dtype=field_names)[0]

        if self._input_mapping:
            collected_entry = {}
            for model_name, signal_name in self._input_mapping.items():
                value = self._read_cache(signal_name)
                if value is not None:
                    collected_entry[model_name] = value

            return dict_to_nparray(collected_entry)

        return dict_to_nparray(self._input)

    async def _sub(self, bus: CanNamespace, mappings: dict):
        signal_names: list[str] = []
        for _model_name, signal_name in mappings.items():
            signal_names.append(signal_name)

        async for signals_batch in await bus.subscribe(*signal_names):
            for signal in signals_batch:
                self._read_cache[signal.name] = signal.value

    async def run(self, bus: CanNamespace) -> asyncio.Task:
        """Run model until stop time or forever when run_forever=True"""
        if self._input_mapping:
            self._sub_task = asyncio.create_task(self._sub(bus, self._input_mapping))
        return run_all(bus, [self])

    async def step(self, bus: CanNamespace) -> None:
        """Advance the simulation by a given step time, applying dynamic inputs if provided.

        Args:
            bus: The CanNamespace the fmu run on
        """
        if self._reached_end:
            return

        def get_step_finished_callback(pause_time):
            # Define the condition to pause simulation at the desired time
            return lambda time, _recorder: time < pause_time

        # Set up the parameters for simulate_fmu
        self._simulation_kwargs["step_finished"] = get_step_finished_callback(
            self._simulation_kwargs["start_time"] + self._simulation_kwargs["output_interval"]
        )
        self._simulation_kwargs["input"] = self._make_input()

        # Run the simulation step with the current parameters and inputs
        result = simulate_fmu(**self._simulation_kwargs)
        # Update the internal state after the step
        self._simulation_kwargs["start_time"] += self._simulation_kwargs["output_interval"]
        self._simulation_kwargs["fmu_state"] = self._simulation_kwargs["fmu_instance"].getFMUState()

        self._last_entry = result[-1]
        await self._publish(self._last_entry, bus)

        await self._notify_next_step()

        # Check if the simulation has reached the stop time
        if self._stop_time is not None and self._last_entry["time"] > self._stop_time:
            _logger.info(f"model reached end at {self._stop_time}")
            self._reached_end = True

    def get_output(self) -> dict[str, Any]:
        """Get all output values of the last step"""
        result = {}
        for key in self._last_entry.dtype.names if hasattr(self._last_entry, "dtype") else self._last_entry:
            result[key] = self._last_entry[key]
        return result

    async def _publish(self, data: None | dict, bus: CanNamespace) -> None:
        """Publishes each key-value pair from last_entry using the mapping table.

        Args:
            last_entry (numpy.void or dict): The data entry containing the keys and values.
            bus: The CanNamespace the fmu run on
        """
        output_mapping = self._output_mapping
        if not output_mapping or data is None:
            return

        for key in data.dtype.names if hasattr(data, "dtype") else data:
            if key in output_mapping:
                value = data[key]
                mapping_value = output_mapping[key]
                await bus.restbus.update_signals(RestbusSignalConfig(name=mapping_value, loop=[value]))


# fix: add functionality to transfer outputs from one model to the next
def run_all(bus: CanNamespace, models: List[FMUModel]) -> asyncio.Task:
    """Run several models in sync assuming they have the same step_size.
    Models are run until stop time or forever when run_forever=True"""

    async def on_tick(elapsed_time: float, since_last_tick: float, total_drift: float, interval: float) -> None:  # noqa: ARG001
        for model in models:
            await model.step(bus)

    for model in models:
        if model.get_step_size() != models[0].get_step_size():
            raise UnsupportedFMUModelError("Step size must be the same")

    # fix: the ticker and simulation context should probably use the same asyncio loop
    async def runner():
        ticker_task = create_ticker(models[0].get_step_size(), on_tick)
        tasks = [ticker_task] + [m._sub_task for m in models if m._sub_task is not None]
        await asyncio.gather(*tasks)

    return asyncio.create_task(runner())
