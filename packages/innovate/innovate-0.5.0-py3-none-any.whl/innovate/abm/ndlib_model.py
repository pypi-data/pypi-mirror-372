from typing import Optional

import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import networkx as nx
from mesa import Model

from .agent import InnovationAgent


class NDlibModel(Model):
    """An innovation diffusion model using ndlib for network-based simulations."""

    def __init__(
        self,
        num_agents,
        graph: Optional[nx.Graph] = None,
        model_name: str = "ic",
    ):
        """Initialize the NDlibModel with a specified number of agents, network graph, and diffusion model type.

        Creates a network-based innovation diffusion simulation by assigning agents to nodes in the provided or generated graph and initializing the chosen NDlib diffusion model. The initial state marks node 0 as 'Infected' (adopted). Supported diffusion models are Independent Cascades ("ic"), Linear Threshold ("lt"), SIR ("sir"), and SIS ("sis").

        Parameters
        ----------
            num_agents (int): Number of agents (nodes) in the simulation.
            graph (nx.Graph, optional): NetworkX graph to use for the simulation. If None, an Erdős-Rényi random graph is generated.
            model_name (str, optional): Name of the diffusion model to use ("ic", "lt", "sir", or "sis"). Defaults to "ic".

        Raises
        ------
            ValueError: If an unsupported model_name is provided.
        """
        super().__init__()
        self.num_agents = num_agents
        self.running = True

        # Create a networkx graph if one is not provided
        if graph is None:
            self.graph = nx.erdos_renyi_graph(n=self.num_agents, p=0.1)
        else:
            self.graph = graph

        # Create agents and add them as nodes to the graph
        for i in range(self.num_agents):
            agent = InnovationAgent(unique_id=i, model=self)
            self.graph.nodes[i]["agent"] = agent

        # Initialize the ndlib diffusion model
        if model_name == "ic":
            self.diffusion_model = ep.IndependentCascadesModel(self.graph)
        elif model_name == "lt":
            self.diffusion_model = ep.ThresholdModel(self.graph)
        elif model_name == "sir":
            self.diffusion_model = ep.SIRModel(self.graph)
        elif model_name == "sis":
            self.diffusion_model = ep.SISModel(self.graph)
        else:
            raise ValueError(f"Unknown model name: {model_name}")

        # Set up the initial state of the diffusion model using a
        # Configuration object. Infect a single node to start the cascade.
        config = mc.Configuration()
        config.add_model_initial_configuration("Infected", [0])
        self.diffusion_model.set_initial_status(config)

    def step(self):
        """Run one step of the diffusion model."""
        self.diffusion_model.iteration()

        # Update the state of the Mesa agents based on the ndlib model
        for node_id, status in self.diffusion_model.status.items():
            agent = self.graph.nodes[node_id]["agent"]
            if status == "Infected":
                agent.adopted = True
