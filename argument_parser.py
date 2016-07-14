# -*- coding: utf-8 -*-
import argparse


class OptionsSolverArgumentParser(object):

    @staticmethod
    def get_parser():
        parser = argparse.ArgumentParser(
            description="Calculates options prices"
        )
        parser.add_argument(
            '--type', '-t', choices=['europian', 'asian'],
            required=True, help="Option type"
        )
        parser.add_argument(
            '--fdm_type', '-mt', choices=['explicit', 'implicit'],
            required=True, help="Finite difference method type"
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
        return parser
