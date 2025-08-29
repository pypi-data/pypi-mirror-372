from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

from .agent import InnovationAgent


class SentimentHypeAgent(InnovationAgent):
    """An agent in a sentiment-driven hype cycle model.
    The agent's adoption decision is influenced by sentiment.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sentiment = 0  # -1 for negative, 0 for neutral, 1 for positive

    def step(self):
        """The agent's step function.
        The agent's decision to adopt is based on its neighbors' adoptions and sentiment.
        """
        if self.adopted:
            return

        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=True,
            include_center=False,
        )
        if not neighbors:
            return

        # Example logic: adopt if enough neighbors have adopted and sentiment is positive
        adopting_neighbors = [n for n in neighbors if n.adopted]
        positive_sentiment_neighbors = [n for n in neighbors if n.sentiment > 0]

        if (
            len(adopting_neighbors) > self.model.adoption_threshold
            and len(positive_sentiment_neighbors) > self.model.sentiment_threshold
        ):
            self.adopted = True


class SentimentHypeModel(Model):
    """A model for a sentiment-driven hype cycle."""

    def __init__(
        self,
        num_agents,
        width,
        height,
        adoption_threshold,
        sentiment_threshold,
    ):
        super().__init__()
        self.num_agents = num_agents
        self.adoption_threshold = adoption_threshold
        self.sentiment_threshold = sentiment_threshold
        self.grid = MultiGrid(width, height, True)
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            agent = SentimentHypeAgent(unique_id=i, model=self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # Seed initial adopters and sentiment
        for _ in range(5):  # Seed 5 initial adopters
            agent = self.random.choice(list(self.agents))
            agent.adopted = True
            agent.sentiment = 1

        self.datacollector = DataCollector(
            model_reporters={
                "Adopters": lambda m: sum([1 for a in m.agents if a.adopted]),
            },
        )

    def step(self):
        """Run one step of the model."""
        self.datacollector.collect(self)
        self.agents.do("step")

    def run_model(self, n_steps):
        """Run the model for a specified number of steps."""
        for _ in range(n_steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()
