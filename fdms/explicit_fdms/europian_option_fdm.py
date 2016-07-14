# -*- coding: utf-8 -*-

import math

import numpy as np

from ..core import FDMBaseEuropian


class EuropianOptionExplicitFDM(FDMBaseEuropian):
    """
    Explicit Euler scheme realization for Black-Scholes PDE
    for vanilla europian option
    """
    def get_fdm_coefficients(self):
        """
        C_j^{n+1} = alpha * C_{j-1}^n + beta * C_j^n + gamma * C_{j+1}^n
        :return: FDM coefficients
        """
        j_nodes = np.arange(0, len(self.nodes.asset_price_nodes))
        alpha = (
            -self.market.interest * j_nodes / 2.0 * self.dt +
            self.market.volatility**2 * j_nodes**2 / 2.0 * self.dt
        )
        beta = (
            1 - (self.market.volatility**2 * j_nodes**2 +
                 self.market.interest) * self.dt
        )
        gamma = (
            (self.market.interest + self.market.volatility**2 * j_nodes) *
            j_nodes * self.dt / 2.0
        )
        return alpha, beta, gamma

    def calculate_prices(self):
        time_nodes_count = len(self.nodes.time_nodes)
        asset_price_nodes_count = len(self.nodes.asset_price_nodes)
        C_0 = [
            self.option.calculate_payoff(price)
            for price in self.nodes.asset_price_nodes
        ]
        C = np.zeros(
            (time_nodes_count, asset_price_nodes_count)
        )
        C[0] = C_0
        alpha, beta, gamma = self.get_fdm_coefficients()

        for step in range(1, time_nodes_count):
            time = self.option.maturity - step * self.dt
            tau = self.option.maturity - time
            C_next = (
                alpha[1:-1] * C[step - 1][0:-2] +
                beta[1:-1] * C[step - 1][1:-1] +
                gamma[1:-1] * C[step - 1][2:]
            )
            C_next = (
                [0.0] + list(C_next) +
                [self.nodes.asset_price_nodes[-1] -
                    self.option.strike *
                    math.exp(-self.market.interest * tau)]
            )
            C[step] = np.array(C_next)

        self.option_prices = C
        return self.option_prices
