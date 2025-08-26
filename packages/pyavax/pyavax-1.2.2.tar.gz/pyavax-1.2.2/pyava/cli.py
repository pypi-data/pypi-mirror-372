import sys
import asyncio
from .utils import run_package_name_checker, print_banner
from pyglow.pyglow import Glow
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(
        description="pyava is a command line tool to help you check the availability of a package name you want on pypi.org"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="pyava Version 1.2.0",
        help="Show pyava version"
    )

    parser.add_argument(
        "package_names",
        nargs="+",
        help="A package name(s) list you want to check (Maximum 5)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds for each request"
    )

    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Don't show additional information about the package. just the status(Available or Taken)"
    )

    if len(sys.argv) == 1:
        print_banner()

    arguments = parser.parse_args()

    if len(arguments.package_names) > 5:
        Glow.prints("⚠️ Warning: You can only check up to 5 package names at a time.", "Yellow Italic")
        arguments.package_names = arguments.package_names[:5]

    try:
        asyncio.run(run_package_name_checker(arguments.package_names, arguments.timeout, arguments.silent))
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
