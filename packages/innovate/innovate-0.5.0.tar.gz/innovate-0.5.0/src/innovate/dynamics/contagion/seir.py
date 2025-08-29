from .base import ContagionSpread


class SEIRModel(ContagionSpread):
    """Models the spread of a contagion through a population with Susceptible,
    Exposed, Infectious, and Recovered states.
    """

    def compute_spread_rate(self, **params):
        """Calculates the instantaneous spread rate.

        Equations:
        dS/dt = -beta * S * I
        dE/dt = beta * S * I - alpha * E
        dI/dt = alpha * E - gamma * I
        dR/dt = gamma * I

        Compute the instantaneous rates of change for each SEIR compartment based on current state values and model parameters.

        Parameters
        ----------
                S (float): Current number of susceptible individuals.
                E (float): Current number of exposed individuals.
                I (float): Current number of infectious individuals.
                transmission_rate (float, optional): Rate at which susceptible individuals become exposed (default 0.1).
                incubation_rate (float, optional): Rate at which exposed individuals become infectious (default 0.1).
                recovery_rate (float, optional): Rate at which infectious individuals recover (default 0.01).

        Returns
        -------
                tuple: Derivatives (dS/dt, dE/dt, dI/dt, dR/dt) representing the rates of change for susceptible, exposed, infectious, and recovered compartments.
        """
        S = params.get("S")
        E = params.get("E")
        I = params.get("I")
        beta = params.get("transmission_rate", 0.1)
        alpha = params.get("incubation_rate", 0.1)
        gamma = params.get("recovery_rate", 0.01)

        dSdt = -beta * S * I
        dEdt = beta * S * I - alpha * E
        dIdt = alpha * E - gamma * I
        dRdt = gamma * I
        return dSdt, dEdt, dIdt, dRdt

    def predict_states(self, time_points, **params):
        """Predicts the states of the population over time.

        Simulates the SEIR model over specified time points and returns the predicted population states.

        Parameters
        ----------
            time_points (array-like): Sequence of time points at which to compute the states.

        Returns
        -------
            ndarray: Array of shape (len(time_points), 4) containing the predicted values for Susceptible, Exposed, Infectious, and Recovered populations at each time point.
        """
        from scipy.integrate import solve_ivp

        S0 = params.get("S0", 999)
        E0 = params.get("E0", 0)
        I0 = params.get("I0", 1)
        R0 = params.get("R0", 0)

        def ode_func(t, y):
            return self.compute_spread_rate(S=y[0], E=y[1], I=y[2], **params)

        sol = solve_ivp(
            ode_func,
            (time_points[0], time_points[-1]),
            [S0, E0, I0, R0],
            t_eval=time_points,
            method="LSODA",
        )
        return sol.y.T

    def get_parameters_schema(self):
        """Returns the schema for the model's parameters.

        Return a dictionary describing the schema for SEIR model parameters, including types, default values, and descriptions for each parameter.

        Returns
        -------
            dict: A mapping of parameter names to their type, default value, and description.
        """
        return {
            "transmission_rate": {
                "type": "float",
                "default": 0.1,
                "description": "The rate of transmission of the contagion.",
            },
            "incubation_rate": {
                "type": "float",
                "default": 0.1,
                "description": "The rate at which exposed individuals become infectious.",
            },
            "recovery_rate": {
                "type": "float",
                "default": 0.01,
                "description": "The rate of recovery from the contagion.",
            },
            "S0": {
                "type": "float",
                "default": 999,
                "description": "The initial number of susceptible individuals.",
            },
            "E0": {
                "type": "float",
                "default": 0,
                "description": "The initial number of exposed individuals.",
            },
            "I0": {
                "type": "float",
                "default": 1,
                "description": "The initial number of infectious individuals.",
            },
            "R0": {
                "type": "float",
                "default": 0,
                "description": "The initial number of recovered individuals.",
            },
        }
