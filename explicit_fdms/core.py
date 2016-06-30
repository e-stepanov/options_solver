# -*- coding: utf-8 -*-

import numpy as np


class ExplicitFDMBase(object):
    """
    Base class for explicit schemes realizations for different options pricing
    """
    def __init__(self, option, market, nodes):
        self.nodes = nodes
        self.option = option
        self.market = market

    def calculate_prices(self):
        raise NotImplementedError

    def plot_option_prices(self, sparse_coordinates):
        raise NotImplementedError


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
