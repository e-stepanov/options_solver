# -*- coding: utf-8 -*-
import math

import numpy as np


class MarketData(object):

    def __init__(self, interest, volatility):

        self.interest = interest
        self.volatility = volatility


class Option(object):

    def __init__(self, strike, maturity, *args, **kwargs):
        self.strike = strike
        self.maturity = maturity

    def calculate_payoff(self, *args, **kwargs):
        raise NotImplementedError


class EuropianOption(Option):

    def calculate_payoff(self, asset_price):
        return np.maximum(asset_price - self.strike, 0)

    def calculate_price(self, asset_price, market_data):
        d1 = (
            (np.log(asset_price / self.strike) +
                (market_data.interest +
                    market_data.volatility**2 / 2.0) *
                self.maturity) /
            (market_data.volatility * np.sqrt(self.maturity))
        )
        d2 = d1 - market_data.volatility * np.sqrt(self.maturity)
        option_price = (
            asset_price * (self._cdf(d1)) - self.strike *
            np.exp(-market_data.interest * self.maturity) *
            self._cdf(d2)
        )
        return option_price

    def _cdf(self, x):
        """
        Calculate cumulative distribution function in a certain point
        """
        if isinstance(x, float):
            return 1.0 / 2.0 * (1 + math.erf(x / np.sqrt(2)))
        else:
            return (
                1.0 / 2.0 *
                (1 + np.array([math.erf(n / np.sqrt(2)) for n in x]))
            )


class AsianOption(Option):

    def calculate_payoff(self, average_price):
        return np.maximum(average_price / self.maturity - self.strike, 0)


if __name__ == "__main__":
    # test
    S = 100.0
    K = 100.0
    r = 0.05
    sigma = 0.2
    T = 1.0

    market = MarketData(r, sigma)
    price = EuropianOption(K, T).calculate_price(S, market)

    assert abs(price - 10.4506) < 10**(-4)
