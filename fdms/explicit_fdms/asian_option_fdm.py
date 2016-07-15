# -*- coding: utf-8 -*-

import time

import numpy as np

from ..core import FDMBase


class AsianOptionExplicitFDM(FDMBase):
    """
    Explicit Euler scheme realization for Black-Scholes PDE
    for vanilla europian option
    """

    def __init__(self, option, market, nodes):
        # fdm parameters
        super(AsianOptionExplicitFDM, self).__init__(option, market, nodes)

        self._t_nodes = self.nodes.time_nodes
        self._S_nodes = self.nodes.asset_price_nodes
        self._A_nodes = self.nodes.average_price_nodes

        self._t_number = len(self.nodes.time_nodes)
        self._S_number = len(
            self.nodes.asset_price_nodes
        )
        self._A_number = len(
            self.nodes.average_price_nodes
        )

        self.dt = (
            self.nodes.time_nodes[1] - self.nodes.time_nodes[0]
        )
        self.dS = (
            self.nodes.asset_price_nodes[1] -
            self.nodes.asset_price_nodes[0]
        )
        self.dA = (
            self.nodes.average_price_nodes[1] -
            self.nodes.average_price_nodes[0]
        )

    # BOUNDARY VALUES

    def get_boundary_left(self, time_node):
        """ Boundary values for S = 0 """
        return (
            np.exp(-self.market.interest * time_node) *
            self.option.calculate_payoff(self._A_nodes)
        )

    def get_boundary_right(self, time_node):
        """ Boundary values for S = S_max """
        return (
            np.maximum(
                np.exp(-self.market.interest * time_node) *
                (self._A_nodes / self.option.maturity -
                 self.option.strike) +
                self._S_nodes[-1] /
                (self.market.interest * self.option.maturity) *
                (1.0 - np.exp(-self.market.interest * time_node)), 0
            )
        )

    def get_boundary_front(self, C_j1):
        """ Boundary values for A = 0 """
        return C_j1

    def get_boundary_back(self, time_node):
        """ Boundary values for A = A_max"""
        return (
            np.exp(-self.market.interest * time_node) *
            self.option.calculate_payoff(
                self._A_nodes[-1]
            ) +
            self._S_nodes / (self.market.interest * self.option.maturity) *
            (1 - np.exp(-self.market.interest * time_node))
        )

    # INITIAL VALUES
    def get_initial(self):
        """ Initial values of option prices (tau = 0) """
        return np.tile(
            self.option.calculate_payoff(self._A_nodes),
            (self._S_number, 1)
        )

    # COEFFICIENTS OF FINITE DIFFERENCE SCHEME
    def get_coeffs_center(self):
        """ Coefficients for C_jk """
        return (
            1 - self.dt * (np.arange(
                self._S_number)**2 *
                self.market.volatility**2 / 2.0 + self.market.interest)
        )

    def get_coeffs_right(self):
        """ Coefficients for C_{j+1,k} """
        S_range = np.arange(self._S_number)
        return (
            self.dt / 2.0 * (S_range**2 * self.market.volatility**2 / 2.0 +
                             S_range * self.market.interest)
        )

    def get_coeffs_left(self):
        """ Coefficients for C_{j-1,k} """
        S_range = np.arange(self._S_number)
        return self.dt / 2.0 * (S_range**2 * self.market.volatility**2 / 2.0 -
                                S_range * self.market.interest)

    def get_coeffs_front(self):
        """ Coefficients for C_{j,k+1} """
        return (
            np.arange(self._S_number) *
            self.dS * self.dt / (2.0 * self.dA)
        )

    def get_coeffs_back(self):
        """ Coefficients for C_{j,k-1} """
        return (
            -np.arange(self._S_number) *
            self.dS * self.dt / (2.0 * self.dA)
        )

    def write_to_file(self, C, filename):
        """ Write computed values to file """
        f = open(filename, 'w')
        for i in range(self._S_number):
            for j in range(self._A_number):
                f.write("%s %s %s\n" % (
                    self._S_nodes[i], self._A_nodes[j], C[i, j]
                ))

    def get_zero_volatility_solution(self):
        """ Return precise solution for zero volatility at tau = T """
        A_grid, S_grid = np.meshgrid(self._A_nodes, self._S_nodes)
        return np.maximum(
            (A_grid / self.option.maturity - self.option.strike_price) *
            np.exp(-self.market.interest * self.option.maturity) +
            S_grid / (self.market.interest * self.option.maturity) *
            (1 - np.exp(-self.market.interest * self.option.maturity)), 0
        )

    def calculate_prices(self):
        start = time.time()
        print("Begin: %s" % str(time.time() - start))

        coeffs_center = self.get_coeffs_center()
        coeffs_right = self.get_coeffs_right()
        coeffs_left = self.get_coeffs_left()
        coeffs_front = self.get_coeffs_front()
        coeffs_back = self.get_coeffs_back()

        print(
            "Coeffs were counted succesfully: %s" %
            str(time.time() - start)
        )

        C_next = np.zeros((self._S_number, self._A_number))
        C_current = self.get_initial()

        for time_node in self.nodes.time_nodes[1:]:
            # every 100th iteration print time info
            if not int(time_node * self._t_number) % 100:
                print(
                    "tau = %s. Time elapsed: %s" %
                    (time_node, str(time.time() - start))
                )
                print(
                    "Minimum value %f" % np.min(C_current)
                )

            # values inside the area
            C_next[1:self._S_number - 1, 1:self._A_number - 1] = (
                C_current[1:self._S_number - 1,
                          1:self._A_number - 1] *
                coeffs_center[1:self._S_number - 1, np.newaxis] +
                C_current[0:self._S_number - 2,
                          1:self._A_number - 1] *
                coeffs_left[1:self._S_number - 1, np.newaxis] +
                C_current[2:self._S_number, 1:self._A_number - 1] *
                coeffs_right[1:self._S_number - 1, np.newaxis] +
                C_current[1:self._S_number - 1,
                          0:self._A_number - 2] *
                coeffs_back[1:self._S_number - 1, np.newaxis] +
                C_current[1:self._S_number - 1, 2:self._A_number] *
                coeffs_front[1:self._S_number - 1, np.newaxis]
            )

            # boundary values
            C_next[0] = (  # S = 0
                self.get_boundary_left(time_node)
            )
            C_next[self._S_number - 1] = (  # S = S_max
                self.get_boundary_right(time_node)
            )
            C_next[:, 0] = (  # A = 0
                self.get_boundary_front(C_next[:, 1])
            )
            C_next[:, self._A_number - 1] = (  # A = A_max
                self.get_boundary_back(time_node)
            )
            C_current = C_next.copy()

        return C_current
