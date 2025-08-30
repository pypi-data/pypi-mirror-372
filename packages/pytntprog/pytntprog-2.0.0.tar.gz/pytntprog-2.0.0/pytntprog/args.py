"""
pygitscrum argparse gestion
"""

import argparse
import sys


def compute_args():
    """
    check args and return them
    """
    my_parser = argparse.ArgumentParser(
        description="pytntprog displays the program of tnt tv in France",
        epilog="""
        Full documentation at: <https://github.com/thib1984/pytntprog>.
        Report bugs to <https://github.com/thib1984/pytntprog/issues>.
        MIT Licence.
        Copyright (c) 2021 thib1984.
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.
        Written by thib1984.""",
    )
    my_parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="update pytntprog",
    )
    my_parser.add_argument(
        "-i",
        "--id",
        type=str,
        help="show full details for id programm",
    )
    my_parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=0,
        help="duree minimale en minute",
    )           
    my_parser.add_argument(
        "-f",
        "--filter",
        action="store",
        nargs="+",
        type=str,
        help="cumultative filter the results",
    )
    my_parser.add_argument(
        "-F",
        "--Filter",
        action="store",
        nargs="+",
        type=str,
        help="cumultative filter-full the results",
    )    
    my_parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="display all days results (current day by default)",
    )        
    my_parser.add_argument(
        "-C",
        "--cache",
        action="store_true",
        help="download the xml file even if the cache is not finished (24 hours by default)",
    ) 
    my_parser.add_argument(
        "-c",
        "--current",
        action="store_true",
        help="current programm",
    )
    my_parser.add_argument(
        "-n",
        "--nocolor",
        action="store_true",
        help="disable color in sysout",
    )                 
    args = my_parser.parse_args()
    return args
