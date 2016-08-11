# -*- coding: utf-8 -*-
""" Base classes for finite difference schemes realizations """

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


class FDMBase(object):
    """
    Base class for finite difference schemes realizations for
    different options pricing
    """
    def __init__(self, option, market, nodes):
        self.nodes = nodes
        self.option = option
        self.market = market

    def calculate_prices(self):
        raise NotImplementedError

    def plot_option_prices(self, sparse_coordinates):
        raise NotImplementedError


class FDMBaseEuropian(FDMBase):
    """
    Base class for finite difference schemes realizations for
    europian options pricing
    """
    def __init__(self, option, market, nodes):
        super(FDMBaseEuropian, self).__init__(
            option, market, nodes
        )
        self.dt = self.nodes.time_nodes[1] - self.nodes.time_nodes[0]

    def plot_option_prices(self, time_sparse=1, asset_price_sparse=1):
        """
        Plot option prices with respect to time and initial asset price
        """
        asset_prices_grid, time_grid = np.meshgrid(
            self.nodes.asset_price_nodes[::asset_price_sparse],
            self.nodes.time_nodes[::time_sparse]
        )
        figure = plt.figure()
        axes = Axes3D(figure)
        axes.plot_surface(
            time_grid, asset_prices_grid,
            self.option_prices[::time_sparse, ::asset_price_sparse],
            rstride=1, cstride=1, cmap=cm.YlGnBu_r
        )
        plt.show()

    def compare_with_analytical(self, show_plot=False):
        """
        Compare numerical solution with analytical
        """
        if not hasattr(self, 'option_prices'):
            raise AttributeError(
                'Option prices not calculated yet.'
                ' Run calculate_prices method firstly'
            )

        prices_analytical = self.option.calculate_price(
            self.nodes.asset_price_nodes, self.market
        )
        prices_numerical = self.option_prices[-1][:]

        max_error = np.max(np.abs(prices_analytical - prices_numerical))
        max_error_index = np.argmax(
            np.abs(prices_analytical - prices_numerical)
        )

        print("Max error: %f" % max_error)
        print("Analitycal price: %f" % prices_analytical[max_error_index])
        print("Numerical price: %f" % prices_numerical[max_error_index])

        if show_plot:
            plt.figure(1)
            plt.subplot(211)
            plt.plot(self.nodes.asset_price_nodes, prices_analytical)
            plt.subplot(212)
            plt.plot(self.nodes.asset_price_nodes, prices_numerical)
            plt.show()


class Nodes(object):
    def __init__(self, nodes_data):
        """
        nodes_data is a list of tuples of the following form:
        (nodes_interval, number_of_points, var_name),
        for example:
        ([0.0, 100.0], 1000, 'time')
        """
        for interval, nodes_count, name in nodes_data:
            nodes = np.linspace(
                interval[0], interval[1], nodes_count
            )
            setattr(
                self, "%s_nodes" % name, nodes
            )
            setattr(
                self, "%s_interval" % name, interval
            )
            setattr(
                self, "%s_nodes_count" % name, nodes_count
            )
