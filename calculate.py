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
        if args.fdm_type == 'explicit':
            fdm_class = EuropianOptionExplicitFDM
        elif args.fdm_type == 'implicit':
            fdm_class = EuropianOptionImplicitFDM
        start_time = time.time()
        option = EuropianOption(
            strike=args.strike, maturity=args.maturity
        )
        nodes = Nodes([
            ([0.0, args.maturity], 1225, 'time'),
            ([args.asset_price_min, args.asset_price_max],
             3500, 'asset_price')
        ])

        fdm = fdm_class(
            option, market_data, nodes
        )

        prices = fdm.calculate_prices()
        end_time = time.time()

        print("Executing time %f" % (end_time - start_time))

        fdm.compare_with_analytical(show_plot=True)

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
