import argparse
import sys


class PrintVersionExitAction(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):  # noqa: A002
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):  # noqa: ARG002
        from dcaspt2_input_generator.__about__ import __version__

        print(f"{__version__}")
        sys.exit()


def parse_args() -> "argparse.Namespace":
    parser = argparse.ArgumentParser(
        description="Load DIRAC output or sum_dirac_dfcoef output and create input file for DIRAC-CASPT2 calculation."
    )
    parser.add_argument("-v", "--version", action=PrintVersionExitAction, help="Print version and exit", dest="version")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print debug output (Normalization constant, Sum of MO coefficient)",
        dest="debug",
    )
    # If -v or --version option is used, print version and exit
    return parser.parse_args()


args = parse_args()
