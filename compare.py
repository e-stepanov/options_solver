# -*- encoding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Calculate options' prices.

Example command for calculating europian option:
python calculate.py -t europian -mt implicit -s 150.0 -m 1.0 -i 0.05 \
 -v 0.01 -smax 350.0

Example command for calculating asian option:
python calculate.py -t asian -tm explicit -s 150.0 -m 1.0 -i 0.05 \
 -v 0.01 -smax 350.0
-amax 200.0

"""
import time

import numpy as np
import matplotlib.pyplot as plt

from market import (
    MarketData,
    EuropianOption,
    AsianOption
)
from fdms.core import Nodes
from fdms.explicit_fdms import (
    EuropianOptionExplicitFDM,
    AsianOptionExplicitFDM
)
from fdms.implicit_fdms import EuropianOptionImplicitFDM
from argument_parser import OptionsSolverArgumentParser


if __name__ == "__main__":
    parser = OptionsSolverArgumentParser.get_parser()
    args = parser.parse_args()

    market_data = MarketData(
        interest=args.interest, volatility=args.volatility
    )

    if args.type == 'europian':
        option = EuropianOption(
            strike=args.strike, maturity=args.maturity
        )
        nodes = Nodes([
            ([0.0, args.maturity], 800, 'time'),
            ([args.asset_price_min, args.asset_price_max],
             3500, 'asset_price')
        ])
        prices_analytical = option.calculate_price(
            nodes.asset_price_nodes, market_data
        )

        prices_numerical = {}
        max_errors = {}
        for fdm_class in [
            EuropianOptionExplicitFDM, EuropianOptionImplicitFDM
        ]:
            start_time = time.time()

            fdm = fdm_class(
                option, market_data, nodes
            )

            prices_numerical[fdm_class.__name__] = (
                fdm.calculate_prices()[-1][:]
            )
            end_time = time.time()

            print("Executing time for %s %f" % (
                fdm_class.__name__, (end_time - start_time)
            ))
            max_errors[fdm_class.__name__] = np.max(
                np.abs(
                    prices_analytical - prices_numerical[fdm_class.__name__]
                )
            )
            print("Max error for %s: %f" % (
                fdm_class.__name__, max_errors[fdm_class.__name__]
            ))

        plt.figure(1)
        plt.subplot(311)
        plt.plot(
            nodes.asset_price_nodes, prices_analytical
        )
        plt.subplot(312)
        plt.plot(
            nodes.asset_price_nodes,
            prices_numerical[EuropianOptionExplicitFDM.__name__]
        )
        plt.subplot(313)
        plt.plot(
            nodes.asset_price_nodes,
            prices_numerical[EuropianOptionImplicitFDM.__name__]
        )
        plt.show()

    elif args.type == 'asian':
        start_time = time.time()
        option = AsianOption(
            strike=args.strike, maturity=args.maturity
        )
        nodes = Nodes([
            ([0.0, args.maturity], 100, 'time'),
            ([args.asset_price_min, args.asset_price_max],
             100, 'asset_price'),
            ([args.average_price_min, args.average_price_max],
             100, 'average_price')
        ])

        fdm = AsianOptionExplicitFDM(
            option, market_data, nodes
        )

        prices = fdm.calculate_prices()
        end_time = time.time()
        print("Executing time %f" % (end_time - start_time))
        print(prices[-1])
    else:
        raise ValueError(
            "Only europian and asian options are supported at this moment"
        )
