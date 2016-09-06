# -*- coding: utf-8 -*-
""" Parser for console input arguments """
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
        return parser
