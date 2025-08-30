"""
pytntprog init
"""


from pytntprog.args import compute_args
from pytntprog.pytntprog import find
from pytntprog.update import update

def pytntprog():
    """
    pytntprog entry point
    """
    args = compute_args()


    if args.update:
        update()
    else:
        find()
