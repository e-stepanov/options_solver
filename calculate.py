# -*- coding: utf-8 -*-
"""
Calculate options' prices.

Example command for calculating europian option:
python calculate.py -t europian -mt implicit -s 150.0 -m 1.0 -i 0.05 \
 -v 0.01 -smax 350.0

Example command for calculating asian option:
python calculate.py -t asian -mt explicit -s 150.0 -m 1.0 -i 0.05 \
 -v 0.01 -smax 350.0 -amax 200.0

"""
import os
import time
import ConfigParser

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
    config = ConfigParser.RawConfigParser()
    config.read('config.cfg')
    results_path = config.get('other', 'results_path')

    parser = OptionsSolverArgumentParser.get_parser()
    args = parser.parse_args()

    market_data = MarketData(
        interest=config.getfloat(args.type, 'interest_rate'),
        volatility=config.getfloat(args.type, 'volatility')
    )

    if args.type == 'europian':
        method_type = config.get(args.type, 'method_type')
        strike = config.getfloat(args.type, 'strike_price')
        maturity = config.getfloat(args.type, 'maturity')
        time_steps_number = config.getint(args.type, 'time_steps_number')
        asset_price_steps_number = config.getint(
            args.type, 'asset_price_steps_number'
        )
        asset_price_min = config.getfloat(args.type, 'asset_price_min')
        asset_price_max = config.getfloat(args.type, 'asset_price_max')

        if method_type == 'explicit':
            fdm_class = EuropianOptionExplicitFDM
        elif method_type == 'implicit':
            fdm_class = EuropianOptionImplicitFDM
        start_time = time.time()
        option = EuropianOption(
            strike=strike, maturity=maturity
        )
        nodes = Nodes([
            ([0.0, maturity], time_steps_number, 'time'),
            ([asset_price_min, asset_price_max],
             asset_price_steps_number, 'asset_price')
        ])

        fdm = fdm_class(
            option, market_data, nodes
        )

        prices = fdm.calculate_prices()
        end_time = time.time()

        fdm.export_to_file(
            os.path.join(
                results_path,
                "europian %d %d.data.xlsx" %
                (time_steps_number, asset_price_steps_number),
            ),
            points_number=100
        )
        fdm.compare_with_analytical()

        print("Executing time %f" % (end_time - start_time))

    elif args.type == 'asian':
        method_type = config.get(args.type, 'method_type')
        strike = config.getfloat(args.type, 'strike_price')
        maturity = config.getfloat(args.type, 'maturity')
        time_steps_number = config.getint(args.type, 'time_steps_number')
        asset_price_steps_number = config.getint(
            args.type, 'asset_price_steps_number'
        )
        average_price_steps_number = config.getint(
            args.type, 'average_price_steps_number'
        )
        asset_price_min = config.getfloat(args.type, 'asset_price_min')
        asset_price_max = config.getfloat(args.type, 'asset_price_max')
        average_price_min = config.getfloat(args.type, 'average_price_min')
        average_price_max = config.getfloat(args.type, 'average_price_max')

        start_time = time.time()
        option = AsianOption(
            strike=strike, maturity=maturity
        )
        nodes = Nodes([
            ([0.0, maturity], time_steps_number, 'time'),
            ([asset_price_min, asset_price_max],
             asset_price_steps_number, 'asset_price'),
            ([average_price_min, average_price_max],
             average_price_steps_number, 'average_price')
        ])

        fdm = AsianOptionExplicitFDM(
            option, market_data, nodes
        )

        prices = fdm.calculate_prices()
        end_time = time.time()
        fdm.plot_option_prices(asset_price_sparse=35, average_price_sparse=20)
        fdm.export_to_file(
            os.path.join(
                results_path,
                "asian_data %d %d %d.xlsx" %
                (time_steps_number, asset_price_steps_number,
                 average_price_steps_number)
            )
        )
        print("Executing time %f" % (end_time - start_time))
    else:
        raise ValueError(
            "Only europian and asian options are supported at this moment"
        )
