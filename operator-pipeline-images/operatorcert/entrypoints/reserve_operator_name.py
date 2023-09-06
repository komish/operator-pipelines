"""Reserve operator name for given combination of association and operator name"""
import argparse
import logging
import sys
from typing import Any
from urllib.parse import urljoin

from operatorcert import pyxis
from operatorcert.logger import setup_logger

LOGGER = logging.getLogger("operator-cert")


def setup_argparser() -> argparse.ArgumentParser:  # pragma: no cover
    """
    Setup argument parser

    Returns:
        Any: Initialized argument parser
    """
    parser = argparse.ArgumentParser(
        description="Reserve the given operator package name"
    )
    parser.add_argument("--association", help="Association of the operator package")
    parser.add_argument("--operator-name", help="Unique name of the operator package")
    parser.add_argument("--source", help="Source of the operator package")
    parser.add_argument(
        "--pyxis-url",
        default="https://pyxis.engineering.redhat.com/",
        help="Base URL for Pyxis container metadata API",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    return parser


def check_operator_name_registered_for_association(args: Any) -> None:
    """
    Check if for given association/isv_pid operatorPackage already exist
    and validates that the package name match operator name requested.
    """
    rsp = pyxis.get(
        urljoin(
            args.pyxis_url,
            "v1/operators/packages?"
            f"filter=association=={args.association};deleted!=true",
        )
    )

    rsp.raise_for_status()

    packages = rsp.json().get("data")

    if packages:
        # there should only be 1 package for given association/isv_pid
        package = packages[0]
        if package["package_name"] != args.operator_name:
            LOGGER.error(
                "Requested operator name %s does not match operator name %s"
                "already reserved for certification project.",
                args.operator_name,
                package["package_name"],
            )
            sys.exit(1)
        else:
            LOGGER.info(
                "Requested operator name %s match "
                "with operator name already reserved.",
                args.operator_name,
            )
    else:
        LOGGER.info(
            "There isn't any operator name registered for project "
            "with association/isv_pid %s",
            args.association,
        )


def check_operator_name(args: Any) -> None:
    """
    Check if operator name already exist and if yes,
    validates if it match with the operator name requested.
    """
    rsp = pyxis.get(
        urljoin(
            args.pyxis_url,
            "v1/operators/packages?"
            f"filter=package_name=={args.operator_name};deleted!=true",
        )
    )

    rsp.raise_for_status()

    packages = rsp.json().get("data")

    if packages:
        # package names are unique, so there should only be 1
        package = packages[0]
        if package["association"] != args.association:
            LOGGER.error(
                "Operator name %s is already taken by another association (%s).",
                args.operator_name,
                package["association"],
            )
            sys.exit(1)
        else:
            LOGGER.info(
                "Operator name %s is already reserved by this association (%s).",
                args.operator_name,
                args.association,
            )
            sys.exit(0)
    else:
        LOGGER.info("Operator name %s is available.", args.operator_name)


def reserve_operator_name(args: Any) -> None:
    """
    Reserve operator name for given combination
    of association and operator name
    """
    post_data = {
        "association": args.association,
        "package_name": args.operator_name,
        "source": args.source,
    }
    pyxis.post(
        urljoin(args.pyxis_url, "v1/operators/packages"),
        post_data,
    )

    LOGGER.info(
        "Operator name %s successfully reserved by %s",
        args.operator_name,
        args.association,
    )


def main() -> None:
    """
    Main function
    """
    parser = setup_argparser()
    args = parser.parse_args()

    log_level = "INFO"
    if args.verbose:
        log_level = "DEBUG"
    setup_logger(level=log_level)

    check_operator_name_registered_for_association(args)
    check_operator_name(args)
    reserve_operator_name(args)


if __name__ == "__main__":  # pragma: no cover
    main()
