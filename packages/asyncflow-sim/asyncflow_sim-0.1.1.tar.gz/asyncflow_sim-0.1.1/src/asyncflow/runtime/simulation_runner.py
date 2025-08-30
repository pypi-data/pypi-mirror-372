"""Components to run the whole simulation given specific input data"""

from __future__ import annotations

from collections import OrderedDict
from itertools import chain
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Protocol, cast

import numpy as np
import simpy
import yaml

from asyncflow.metrics.analyzer import ResultsAnalyzer
from asyncflow.metrics.collector import SampledMetricCollector
from asyncflow.resources.registry import ResourcesRuntime
from asyncflow.runtime.actors.client import ClientRuntime
from asyncflow.runtime.actors.edge import EdgeRuntime
from asyncflow.runtime.actors.load_balancer import LoadBalancerRuntime
from asyncflow.runtime.actors.rqs_generator import RqsGeneratorRuntime
from asyncflow.runtime.actors.server import ServerRuntime
from asyncflow.runtime.events.injection import EventInjectionRuntime
from asyncflow.schemas.payload import SimulationPayload

if TYPE_CHECKING:
    from collections.abc import Iterable

    from asyncflow.schemas.events.injection import EventInjection
    from asyncflow.schemas.topology.edges import Edge
    from asyncflow.schemas.topology.nodes import (
        Client,
        LoadBalancer,
        Server,
    )
    from asyncflow.schemas.workload.rqs_generator import RqsGenerator

# --- PROTOCOL DEFINITION ---
# This is the contract that all runtime actors must follow.
# it is a contract useful to communicate to mypy that object of
# startable type have all the method start
class Startable(Protocol):
    """A protocol for runtime actors that can be started."""

    def start(self) -> simpy.Process:
        """Starts the main process loop for the actor."""
        ...

class SimulationRunner:
    """Class to handle the simulation"""

    def __init__(
        self,
        *,
        env: simpy.Environment,
        simulation_input: SimulationPayload,
        ) -> None:
        """
        Orchestrates building, wiring and running all actor runtimes.

        Args:
            env (simpy.Environment): global environment for the simulation
            simulation_input (SimulationPayload): full input for the simulation

        """
        self.env = env
        self.simulation_input = simulation_input

        # instantiation of object needed to build nodes for the runtime phase
        self.servers: list[Server] = simulation_input.topology_graph.nodes.servers
        self.client: Client = simulation_input.topology_graph.nodes.client
        self.events: list[EventInjection] | None = None
        self.rqs_generator: RqsGenerator = simulation_input.rqs_input
        self.lb: LoadBalancer | None = None
        self.simulation_settings = simulation_input.sim_settings
        self.edges: list[Edge] = simulation_input.topology_graph.edges
        self.rng = np.random.default_rng()

        # Object needed to start the simulation
        self._servers_runtime: dict[str, ServerRuntime] = {}
        self._client_runtime: dict[str, ClientRuntime] = {}
        self._rqs_runtime: dict[str, RqsGeneratorRuntime] = {}
        # right now we allow max one LB per simulation so we don't need a dict
        self._lb_runtime: LoadBalancerRuntime | None = None
        self._edges_runtime: dict[tuple[str, str], EdgeRuntime] = {}
        self._events_runtime: EventInjectionRuntime | None = None

        # Initialization of the OrderedDict used for event injection.
        # This structure allows us to temporarily shut down servers by removing
        # their edges from the load balancer during the simulation. The choice
        # of OrderedDict is motivated by its mutability and O(1) operations for
        # both removal (by key) and moving an element to the end.
        #
        # Advantages of this approach:
        # 1) We allocate a single shared object in memory.
        # 2) The same object is aliased in both LoadBalancerRuntime and
        #    EventInjectionRuntime, so updates are reflected dynamically.
        #
        # Workflow:
        # - Instantiate the OrderedDict here.
        # - Remove edges (LB→server connections) in EventInjectionRuntime
        #   when a server goes down.
        # - Pass the same OrderedDict to LoadBalancerRuntime, which will
        #   apply its algorithm (RR, LeastConnections) only to the currently
        #   available edges.
        #
        # Notes:
        # - Pydantic ensures that at least one server remains available, so the
        #   condition "all servers down" is not allowed.
        # - Shutting down a server by cutting its edge reduces the number of
        #   SimPy processes to manage, because we skip transport to a down
        #   server entirely.
        # - This also avoids extra conditions or policies on the server side to
        #   check whether the server is up or down.

        self._lb_out_edges: OrderedDict[str, EdgeRuntime] = OrderedDict()


    # ------------------------------------------------------------------ #
    # Private: build phase                                               #
    # ------------------------------------------------------------------ #

    def _make_inbox(self) -> simpy.Store:   # local helper
       """Helper to create store for the states of the simulation"""
       return simpy.Store(self.env)

    def _build_rqs_generator(self) -> None:
        """
        Build the rqs generator runtime, we use a dict for one reason
        In the future we might add CDN so we will need
        multiple generators , one for each client
        """
        self._rqs_runtime[self.rqs_generator.id] = RqsGeneratorRuntime(
            env = self.env,
            out_edge=None,
            rqs_generator_data=self.rqs_generator,
            sim_settings=self.simulation_settings,
            rng=self.rng,
        )


    def _build_client(self) -> None:
        """
        Build the client runtime, we use a dict for two reasons
        1) In the future we might add CDN so we will need
           multiple client
        2) When we will assign outer edges we will need a dict
           with all components indexed by their id
        """
        self._client_runtime[self.client.id] = ClientRuntime(
            env=self.env,
            out_edge=None,
            completed_box=self._make_inbox(),
            client_box=self._make_inbox(),
            client_config=self.client,
        )


    def _build_servers(self) -> None:
        """
        Build given the input data a dict containing all server Runtime
        indexed by their unique id
        """
        registry = ResourcesRuntime(
            env=self.env,
            data=self.simulation_input.topology_graph,
        )
        for server in self.servers:
            container = registry[server.id]
            self._servers_runtime[server.id] = ServerRuntime(
                env=self.env,
                server_resources=container,
                server_config=server,
                out_edge=None,
                server_box=self._make_inbox(),
                settings=self.simulation_settings,
                rng= self.rng,

            )


    def _build_load_balancer(self) -> None:
        """
        Build given the input data the load balancer runtime we will
        use a dict because we may have multiple load balancer and we
        will be useful to assign outer edges
        """
        # Topologies without a LB are perfectly legal (e.g. the “minimal”
        # integration test).  Early-return instead of asserting.
        if self.simulation_input.topology_graph.nodes.load_balancer is None:
            return

        self.lb = self.simulation_input.topology_graph.nodes.load_balancer

        self._lb_runtime = LoadBalancerRuntime(
            env=self.env,
            lb_config=self.lb,
            lb_out_edges = self._lb_out_edges,
            lb_box=self._make_inbox(),
        )




    def _build_edges(self) -> None:
        """Initialization of the edges runtime dictionary from the input data"""
        # We need to merge all previous dictionary for the nodes to assign
        # for each edge the correct target box
        all_nodes: dict[str, object] = {
            **self._servers_runtime,
            **self._client_runtime,
            **self._rqs_runtime,
        }

        if self._lb_runtime is not None:
            all_nodes[self._lb_runtime.lb_config.id] = self._lb_runtime

        for edge in self.edges:

            target_object = all_nodes[edge.target]  # O(1) lookup

            if isinstance(target_object, ServerRuntime):
                target_box = target_object.server_box
            elif isinstance(target_object, ClientRuntime):
                target_box = target_object.client_box
            elif isinstance(target_object, LoadBalancerRuntime):
                target_box = target_object.lb_box
            else:
                msg = f"Unknown runtime for {edge.target!r}"
                raise TypeError(msg)


            self._edges_runtime[(edge.source, edge.target)] = (
                EdgeRuntime(
                    env=self.env,
                    edge_config=edge,
                    rng=self.rng,
                    target_box= target_box,
                    settings=self.simulation_settings,
                )
            )
            # Here we assign the outer edges to all nodes
            source_object = all_nodes[edge.source]

            if isinstance(source_object, (
                ServerRuntime,
                ClientRuntime,
                RqsGeneratorRuntime,
                )):
                source_object.out_edge = self._edges_runtime[(
                    edge.source,
                    edge.target)
                ]
            elif isinstance(source_object, LoadBalancerRuntime):
                self._lb_out_edges[edge.id] = (
                    self._edges_runtime[(edge.source, edge.target)]
                )
            else:
                msg =  f"Unknown runtime for {edge.source!r}"
                raise TypeError(msg)



    def _build_events(self) -> None:
        """
        Function to centralize the events logic: with this function
        we attach all events to the components affected
        """
        if not self.simulation_input.events or self._events_runtime is not None:
            return

        self.events = self.simulation_input.events
        self._events_runtime = EventInjectionRuntime(
            events=self.events,
            edges=self.edges,
            env=self.env,
            servers=self.servers,
            lb_out_edges=self._lb_out_edges,
        )

        # container only readable
        edges_affected_view = self._events_runtime.edges_affected

        # only readable map
        edges_spike_view = MappingProxyType(self._events_runtime.edges_spike)

        # We assign the two objects to all edges even though there are no
        # events affecting them, this case is managed in the EdgeRuntime
        # In the future we may control here if an edge is affected from an
        # event this should have some advantage at the level of ram

        for edge in self._edges_runtime.values():
            edge.edges_affected = edges_affected_view
            edge.edges_spike = edges_spike_view



    # ------------------------------------------------------------------ #
    # RUN phase                                                          #
    # ------------------------------------------------------------------ #
    def _start_all_processes(self) -> None:
        """Register every .start() in the environment."""
        # ------------------------------------------------------------------
        # Start every actor's main coroutine
        #
        # * itertools.chain lazily stitches together the four dict_views
        #   into ONE iterator. No temporary list is built, zero extra
        #   allocations, yet the for-loop stays single and readable.
        # * Order matters only for determinism, so we keep the natural
        #   “generator → client → servers → LB” sequence by listing the
        #   dicts explicitly.
        # * Alternative ( list(a)+list(b)+… ) would copy thousands of
        #   references just to throw them away after the loop - wasteful.
        # ------------------------------------------------------------------

        runtimes = chain(
        self._rqs_runtime.values(),
        self._client_runtime.values(),
        self._servers_runtime.values(),
        ([] if self._lb_runtime is None else [self._lb_runtime]),
        )

        # Here we are saying to mypy that those object are of
        # the startable type and they share the start method
        for rt in cast("Iterable[Startable]", runtimes):
            rt.start()


    def _start_metric_collector(self) -> None:
        """One coroutine that snapshots RAM / queues / connections."""
        SampledMetricCollector(
            edges=list(self._edges_runtime.values()),
            servers=list(self._servers_runtime.values()),
            env=self.env,
            sim_settings=self.simulation_settings,
        ).start()


    def _start_events(self) -> None:
        """Function to start the process to build events"""
        if self._events_runtime is not None:
            self._events_runtime.start()



    # ------------------------------------------------------------------ #
    # Public entry-point                                                 #
    # ------------------------------------------------------------------ #
    def run(self) -> ResultsAnalyzer:
        """Build → wire → start → run the clock → return `ResultsAnalyzer`"""
        # 1. BUILD
        self._build_rqs_generator()
        self._build_client()
        self._build_servers()
        self._build_load_balancer()

        # 2. WIRE
        self._build_edges()

        # 3 ATTACH EVENTS TO THE COMPONENTS
        self._build_events()

        # 3. START ALL COROUTINES
        self._start_events()
        self._start_all_processes()
        self._start_metric_collector()

        # 4. ADVANCE THE SIMULATION
        self.env.run(until=self.simulation_settings.total_simulation_time)

        return ResultsAnalyzer(
            client=next(iter(self._client_runtime.values())),
            servers=list(self._servers_runtime.values()),
            edges=list(self._edges_runtime.values()),
            settings=self.simulation_settings,
        )

    # ------------------------------------------------------------------ #
    # Convenience constructor (load from YAML)                           #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_yaml(
        cls,
        *,
        env: simpy.Environment,
        yaml_path: str | Path,
    ) -> SimulationRunner:
        """
        Quick helper so that integration tests & CLI can do:

        ```python
        runner = SimulationRunner.from_yaml(env, "scenario.yml")
        results = runner.run()
        ```
        """
        data = yaml.safe_load(Path(yaml_path).read_text())
        payload = SimulationPayload.model_validate(data)
        return cls(env=env, simulation_input=payload)



