# -*- coding: utf-8 -*-
""" Implicit finite difference scheme for europian options """

import numpy as np

from ..core import FDMBaseEuropian


class EuropianOptionImplicitFDM(FDMBaseEuropian):
    """
    Implicit Euler scheme realization for Black-Scholes PDE
    for vanilla europian option
    """
    @property
    def _coefficients(self):
        j_points = np.arange(1, len(self.nodes.asset_price_nodes) - 1)

        if not hasattr(self, 'alpha_'):
            self.alpha_ = (
                (self.market.interest * j_points -
                 self.market.volatility ** 2 * j_points ** 2) * self.dt / 2.0
            )

        if not hasattr(self, 'beta_'):
            self.beta_ = (
                1 + (self.market.volatility ** 2 * j_points ** 2 +
                     self.market.interest) * self.dt
            )

        if not hasattr(self, 'gamma_'):
            self.gamma_ = (
                -(self.market.interest * j_points +
                  self.market.volatility ** 2 * j_points ** 2) * self.dt / 2.0
            )

        return self.alpha_, self.beta_, self.gamma_

    @property
    def _initial_values(self):
        if not hasattr(self, 'initial_values_'):
            self.initial_values_ = self.option.calculate_payoff(
                self.nodes.asset_price_nodes
            )
        return self.initial_values_

    @property
    def _left_boundary_values(self):
        if not hasattr(self, 'left_boundary_values_'):
            self.left_boundary_values_ = np.array(
                [0.0] * len(self.nodes.time_nodes)
            )
        return self.left_boundary_values_

    @property
    def _right_boundary_values(self):
        if not hasattr(self, 'right_boundary_values_'):
            self.right_boundary_values_ = (
                np.array(
                    [self.nodes.asset_price_nodes[-1]] *
                    len(self.nodes.time_nodes)
                ) -
                self.option.strike *
                np.exp(-self.market.interest * self.nodes.time_nodes)
            )
        return self.right_boundary_values_

    def _get_y(self):
        y = np.zeros(len(self.nodes.asset_price_nodes) - 2)
        y[0] = self._coefficients[1][0]
        for i in range(0, len(y) - 1):
            y[i + 1] = (
                self._coefficients[1][i + 1] - self._coefficients[0][i + 1] *
                self._coefficients[2][i] / y[i]
            )
        return y

    def calculate_prices(self):
        time_nodes_count = len(self.nodes.time_nodes)
        asset_price_nodes_count = len(self.nodes.asset_price_nodes)
        C = np.zeros(
            (time_nodes_count, asset_price_nodes_count)
        )
        q = np.zeros(asset_price_nodes_count - 2)

        C[0] = self._initial_values
        alpha, beta, gamma = self._coefficients
        y = self._get_y()

        C[:, 0] = self._left_boundary_values
        C[:, -1] = self._right_boundary_values

        for time_step in range(1, time_nodes_count):
            q[0] = (
                C[time_step - 1][1] -
                alpha[0] * C[time_step][0]
            )
            for i in range(1, len(q) - 1):
                q[i] = (
                    C[time_step - 1][i + 1] -
                    alpha[i] / y[i - 1] * q[i - 1]
                )
            q[-1] = (
                C[time_step - 1][-2] - gamma[-1] * C[time_step][-1] -
                alpha[-1] / y[-2] * q[-2]
            )

            C[time_step, -2] = (
                q[-1] / y[-1]
            )
            for i in range(asset_price_nodes_count - 3, 0, -1):
                C[time_step, i] = (
                    (q[i - 1] - gamma[i - 1] * C[time_step, i + 1]) / y[i - 1]
                )

        self.option_prices = C
        return self.option_prices
