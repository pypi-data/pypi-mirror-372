from abc import ABC, abstractmethod
from typing import TypeVar

Self = TypeVar("Self")


class ContagionSpread(ABC):
    """Abstract base class for all contagion spread models."""

    @abstractmethod
    def compute_spread_rate(self, **params):
        """Calculates the instantaneous spread rate."""
        """
        Calculate the instantaneous rate at which contagion spreads based on provided model parameters.

        Parameters:
        	params: Arbitrary keyword arguments representing model-specific parameters required to compute the spread rate.

        Returns:
        	The computed spread rate, as defined by the specific contagion model.
        """

    @abstractmethod
    def predict_states(self, time_points, **params):
        """Predicts the states of the population over time."""
        """
        Predict the states of the population at specified time points using the given model parameters.

        Parameters:
            time_points (Iterable): Sequence of time points at which to predict population states.
            **params: Model-specific parameters required for prediction.

        Returns:
            Any: Predicted population states at each specified time point.
        """

    @abstractmethod
    def get_parameters_schema(self):
        """Returns the schema for the model's parameters.

        Return the schema describing the parameters required by the contagion spread model.

        Returns
        -------
            dict: A schema detailing the expected parameters for the model.
        """
