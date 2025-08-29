# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.

"""Simulation queue management functionality."""

from datetime import datetime
from typing import Optional

from ._client import get_default_client
from ._helpers._timestamp_to_datetime import timestamp_to_datetime
from ._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .types import ProjectID, SimulationID


@ProtoWrapper(simulationpb.SimulationQueueStatus)
class SimulationQueueStatus(ProtoWrapperBase):
    """Represents the status of a queued simulation."""

    project_id: ProjectID
    """The ID of the project to which the simulation belongs."""
    simulation_id: SimulationID
    """The ID of the simulation."""
    name: str
    """The name of the simulation."""
    is_lma: bool
    """Whether this is an LMA simulation."""
    priority: bool
    """Whether this is a priority simulation."""

    _proto: simulationpb.SimulationQueueStatus

    @property
    def creation_time(self) -> datetime:
        """The time when the simulation was created."""
        return timestamp_to_datetime(self._proto.creation_time)

    @property
    def started_time(self) -> Optional[datetime]:
        """The time when the simulation started running, if it has started."""
        if self._proto.HasField("started_time"):
            return timestamp_to_datetime(self._proto.started_time)
        return None


class SimulationStatusQueueIterator:
    """Iterator class for simulation status queue that provides length hint."""

    def __init__(self, page_size: int):
        self._page_size: int = page_size
        self._page_token: str = ""
        self._total_count: Optional[int] = None
        self._current_page: Optional[list[simulationpb.SimulationQueueStatus]] = None
        self._client = get_default_client()
        self._iterated_count: int = 0

    def __iter__(self) -> "SimulationStatusQueueIterator":
        return self

    def __next__(self) -> SimulationQueueStatus:
        if self._current_page is None:
            self._fetch_next_page()

        # _current_page really can't be None here, but this assertion is needed to appease mypy
        assert self._current_page is not None

        if len(self._current_page) == 0:
            if not self._page_token:
                raise StopIteration
            self._fetch_next_page()

        self._iterated_count += 1

        return SimulationQueueStatus(self._current_page.pop(0))

    def _fetch_next_page(self) -> None:
        req = simulationpb.ListQueuedSimulationsRequest(
            page_size=self._page_size, page_token=self._page_token
        )
        res = self._client.ListQueuedSimulations(req)

        self._current_page = list(res.simulations)
        self._page_token = res.next_page_token
        if self._total_count is None:
            self._total_count = res.total_count or 0

    def __length_hint__(self) -> int:
        if self._total_count is None:
            # Fetch first page to get total size if not already fetched
            if self._current_page is None:
                self._fetch_next_page()
        return max(0, (self._total_count or 0) - self._iterated_count)


def iterate_simulation_status_queue(page_size: int = 50) -> SimulationStatusQueueIterator:
    """
    Iterate over all simulations in the scheduling queue for the current account.

    This function is only available for accounts with a Subscription Plan.

    Parameters
    ----------
    page_size : int, optional
        Number of simulations to fetch per page. Defaults to 50, max is 100.

    Returns
    -------
    SimulationStatusQueueIterator
        An iterator that yields SimulationQueueStatus objects one at a time.

    Examples
    --------
    Fetch all queued simulations and filter them for LMA simulations.

    >>> lma_sims = [sim for sim in iterate_simulation_status_queue() if sim.is_lma]
    [SimulationQueueStatus(...), SimulationQueueStatus(...)]

    Lazily fetch simulations.
    (A batch size of 2 is a bad idea in real-world usage, but it helps demonstrate the lazy
    fetching.)

    >>> my_sims = iterate_simulation_status_queue(page_size=2)
    >>> next(my_sims) # first page of simulations is fetched, first simulation is returned.
    SimulationQueueStatus(...)
    >>> next(my_sims) # second simulation is returned from memory.
    SimulationQueueStatus(...)
    >>> next(my_sims) # second page of simulations is fetched, third simulation is returned.
    SimulationQueueStatus(...)
    >>> next(my_sims) # if there are no more simulations, this call raises StopIteration.
    """
    return SimulationStatusQueueIterator(page_size)
