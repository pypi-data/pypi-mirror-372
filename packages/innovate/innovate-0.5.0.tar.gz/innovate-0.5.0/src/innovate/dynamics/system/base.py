from abc import ABC, abstractmethod
from typing import TypeVar

Self = TypeVar("Self")


class SystemBehavior(ABC):
    """Abstract base class for all system behavior models."""

    @abstractmethod
    def compute_behavior_rates(self, **params):
        """Calculates the instantaneous behavior rates.

        Calculate the instantaneous rates of system behavior based on provided parameters.

        Parameters
        ----------
            **params: Arbitrary keyword arguments representing model-specific parameters.

        Returns
        -------
            The computed instantaneous behavior rates, with the format defined by the implementing subclass.
        """

    @abstractmethod
    def predict_states(self, time_points, **params):
        """Predicts the states of the system over time.

        Predict the system's states at specified time points using provided parameters.

        Parameters
        ----------
            time_points: Sequence of time points at which to predict system states.
            **params: Additional model-specific parameters required for prediction.

        Returns
        -------
            Predicted states of the system at each specified time point.
        """

    @abstractmethod
    def get_parameters_schema(self):
        """Returns the schema for the model's parameters.

        Return the schema describing the parameters required by the model.

        Returns
        -------
            dict: A schema defining the expected parameters for the model.
        """
