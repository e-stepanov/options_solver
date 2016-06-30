# -*- coding: utf-8 -*-
"""
Calculate options' prices.

Example command for calculating europian option:
python calculate.py -t europian -s 150.0 -m 1.0 -i 0.05 -v 0.01 -smax 350.0

Example command for calculating asian option:

"""
import time
import argparse

from market import (
    MarketData,
    EuropianOption,
    AsianOption
)
from explicit_fdms.core import Nodes
from explicit_fdms.europian_option_fdm import EuropianOptionExplicitFDM
from explicit_fdms.asian_option_fdm import AsianOptionExplicitFDM

parser = argparse.ArgumentParser(description="Calculates options prices")
parser.add_argument(
    '--type', '-t', choices=['europian', 'asian'],
    required=True, help="Option type"
)
parser.add_argument(
    '--strike', '-s',
    type=float, required=True,
    help="Strike price"
)
parser.add_argument(
    '--maturity', '-m',
    type=float, default=1.0,
    help="Maturity (in years)"
)
parser.add_argument(
    '--interest', '-i',
    type=float, required=True,
    help="Interest rate"
)
parser.add_argument(
    '--volatility', '-v',
    type=float, required=True,
    help="Volatility"
)
parser.add_argument(
    '--asset_price_max', '-smax',
    type=float, required=True,
    help="Asset price maximum value"
)
parser.add_argument(
    '--average_price_max', '-amax', type=float,
    help="Average price maximum value (for asian options only)"
)
parser.add_argument(
    '--asset_price_min', '-smin',
    type=float, default=0.0,
    help="Asset price minimum value"
)
parser.add_argument(
    '--average_price_min', '-amin',
    type=float, default=0.0,
    help="Average price minimum value (for asian options only)"
)

if __name__ == "__main__":
    args = parser.parse_args()

    market_data = MarketData(
        interest=args.interest, volatility=args.volatility
    )

    if args.type == 'europian':
        start_time = time.time()
        option = EuropianOption(
            strike=args.strike, maturity=args.maturity
        )
        nodes = Nodes([
            ([0.0, args.maturity], 1000, 'time'),
            ([args.asset_price_min, args.asset_price_max],
             100, 'asset_price')
        ])

        fdm = EuropianOptionExplicitFDM(
            option, market_data, nodes
        )

        prices = fdm.calculate_prices()
        end_time = time.time()
        print "Executing time %f" % (end_time - start_time)
        print prices[-1]
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
        print "Executing time %f" % (end_time - start_time)
        print prices[-1]
    else:
        raise ValueError("Only europian options are supported at this moment")
