from typing import Dict, Optional, Sequence

import numpy as np

from innovate import backend
from innovate.base.base import DiffusionModel
from innovate.dynamics.growth.dual_influence import DualInfluenceGrowth


class BassModel(DiffusionModel):
    """Implementation of the Bass Diffusion Model.
    This is a wrapper around the DualInfluenceGrowth dynamics model.
    """

    def __init__(
        self,
        covariates: Optional[Sequence[str]] = None,
        t_event: Optional[float] = None,
    ):
        """Initialize the BassModel with optional covariates, a time event, and a DualInfluenceGrowth dynamics model.

        Parameters
        ----------
            covariates (Sequence[str], optional): List of covariate names to include in the model. Defaults to an empty list if not provided.
            t_event (float, optional): The time of a structural break or event. If provided, the model will fit separate parameters for the periods before and after this time.
        """
        self._params: Dict[str, float] = {}
        self.covariates = covariates if covariates else []
        self.t_event = t_event
        self.growth_model = DualInfluenceGrowth()

    @property
    def param_names(self) -> Sequence[str]:
        """Return the list of parameter names for the Bass model, including base parameters and covariate-related coefficients.

        Returns
        -------
            names (Sequence[str]): List of parameter names, with covariate effects included if applicable.
        """
        names = ["p", "q", "m"]
        if self.t_event is not None:
            names.extend(["p_post", "q_post", "m_post"])
        for cov in self.covariates:
            names.extend([f"beta_p_{cov}", f"beta_q_{cov}", f"beta_m_{cov}"])
        return names

    def initial_guesses(
        self,
        t: Sequence[float],
        y: Sequence[float],
    ) -> Dict[str, float]:
        guesses = {
            "p": 0.001,
            "q": 0.1,
            "m": np.max(y) * 1.1,
        }
        if self.t_event is not None:
            guesses.update(
                {
                    "p_post": 0.001,
                    "q_post": 0.1,
                    "m_post": np.max(y) * 1.1,
                },
            )
        for cov in self.covariates:
            guesses[f"beta_p_{cov}"] = 0.0
            guesses[f"beta_q_{cov}"] = 0.0
            guesses[f"beta_m_{cov}"] = 0.0
        return guesses

    def bounds(self, t: Sequence[float], y: Sequence[float]) -> Dict[str, tuple]:
        """Return parameter bounds for the Bass model, including covariate effects.

        Parameters
        ----------
            t (Sequence[float]): Sequence of time points.
            y (Sequence[float]): Observed cumulative adoption values.

        Returns
        -------
            Dict[str, tuple]: Dictionary mapping parameter names to (lower, upper) bounds. Base parameters "p", "q", and "m" have fixed bounds; covariate-related parameters are unbounded.
        """
        bounds = {
            "p": (1e-6, 0.1),
            "q": (1e-6, 1.0),
            "m": (np.max(y), np.inf),
        }
        if self.t_event is not None:
            bounds.update(
                {
                    "p_post": (1e-6, 0.1),
                    "q_post": (1e-6, 1.0),
                    "m_post": (np.max(y), np.inf),
                },
            )
        for cov in self.covariates:
            bounds[f"beta_p_{cov}"] = (-np.inf, np.inf)
            bounds[f"beta_q_{cov}"] = (-np.inf, np.inf)
            bounds[f"beta_m_{cov}"] = (-np.inf, np.inf)
        return bounds

    def predict(
        self,
        t: Sequence[float],
        covariates: Optional[Dict[str, Sequence[float]]] = None,
    ) -> Sequence[float]:
        """Predicts cumulative adoption over time using the Bass diffusion model.

        Parameters
        ----------
            t (Sequence[float]): Sequence of time points at which to predict cumulative adoption.
            covariates (Dict[str, Sequence[float]], optional): Optional time series of covariate values affecting model parameters.

        Returns
        -------
            Sequence[float]: Predicted cumulative adoption at each time point in `t`.

        Raises
        ------
            RuntimeError: If the model parameters have not been set (i.e., the model is not fitted).
        """
        if not self._params:
            raise RuntimeError("Model has not been fitted yet. Call .fit() first.")

        from innovate.backends.jax_backend import JaxBackend

        backend.current_backend = JaxBackend()

        y0 = 1e-6

        # This is a simplification. The predict method should use the growth model's
        # predict_cumulative method, which will require some refactoring of how parameters
        # are handled. For now, we will leave the old implementation.

        params = [self._params[name] for name in self.param_names]

        def ode_func(t, y, args):
            return self.differential_equation(t, y, args, covariates, t)

        sol = backend.current_backend.solve_ode(ode_func, y0, t, tuple(params))
        return sol.flatten()

    def differential_equation(self, t, y, params, covariates, t_eval):
        """Defines the Bass model's differential equation, incorporating covariate effects if provided.

        At each time point, adjusts the innovation, imitation, and market size parameters by linearly combining base values with covariate contributions, then computes the instantaneous growth rate using the underlying DualInfluenceGrowth model.

        Parameters
        ----------
            t: Current time point.
            y: Current cumulative adoption value.
            params: Sequence of model parameters, including base and covariate coefficients.
            covariates: Optional dictionary mapping covariate names to their time series values.
            t_eval: Sequence of time points for covariate interpolation.

        Returns
        -------
            The instantaneous adoption rate at time t.
        """
        if self.t_event is not None and t >= self.t_event:
            p_base = params[3]
            q_base = params[4]
            m_base = params[5]
            param_idx_offset = 3
        else:
            p_base = params[0]
            q_base = params[1]
            m_base = params[2]
            param_idx_offset = 0

        p_t = p_base
        q_t = q_base
        m_t = m_base

        if covariates:
            param_idx = 3 + param_idx_offset
            for cov_name, cov_values in covariates.items():
                cov_val_t = backend.current_backend.interp(t, t_eval, cov_values)

                p_t += params[param_idx] * cov_val_t
                q_t += params[param_idx + 1] * cov_val_t
                m_t += params[param_idx + 2] * cov_val_t
                param_idx += 3

        rate = (p_t + q_t * (y / m_t)) * (m_t - y)
        try:
            import pytensor.tensor as pt  # type: ignore

            if isinstance(
                m_t,
                pt.TensorVariable,
            ):  # pragma: no cover - depends on pytensor
                return pt.switch(m_t > 0, rate, 0.0)
        except Exception:
            pass
        return backend.current_backend.where(m_t > 0, rate, 0.0)

    def score(
        self,
        t: Sequence[float],
        y: Sequence[float],
        covariates: Optional[Dict[str, Sequence[float]]] = None,
    ) -> float:
        """Compute the coefficient of determination (R²) between observed and predicted values.

        Parameters
        ----------
                y (Sequence[float]): Observed cumulative adoption values.

        Returns
        -------
                float: R² score indicating the proportion of variance explained by the model predictions.
        """
        if not self._params:
            raise RuntimeError("Model has not been fitted yet. Call .fit() first.")
        y_pred = self.predict(t, covariates)
        ss_res = backend.current_backend.sum(
            (backend.current_backend.array(y) - y_pred) ** 2,
        )
        ss_tot = backend.current_backend.sum(
            (backend.current_backend.array(y) - backend.current_backend.mean(y)) ** 2,
        )
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    @property
    def params_(self) -> Dict[str, float]:
        return self._params

    @params_.setter
    def params_(self, value: Dict[str, float]):
        self._params = value

    def predict_adoption_rate(
        self,
        t: Sequence[float],
        covariates: Optional[Dict[str, Sequence[float]]] = None,
    ) -> Sequence[float]:
        if not self._params:
            raise RuntimeError("Model has not been fitted yet. Call .fit() first.")

        y_pred = self.predict(t, covariates)
        params = [self._params[name] for name in self.param_names]

        rates = np.array(
            [
                self.differential_equation(ti, yi, params, covariates, t)
                for ti, yi in zip(t, y_pred)
            ],
        )
        return rates

    def cumulative_adoption(self, t: Sequence[float], *params) -> Sequence[float]:
        self.params_ = dict(zip(self.param_names, params))
        return self.predict(t)
