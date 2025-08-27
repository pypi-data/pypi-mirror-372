# Copyright © 2025 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

import argparse
import os
import sys
import shutil

from contrast import __file__
from contrast.configuration.agent_config import AgentConfig
from contrast_rewriter import REWRITE_FOR_PYTEST
from contrast_vendor import structlog as logging


logger = logging.getLogger("contrast")

DESCRIPTION = """
The command-line runner for the Contrast Python Agent.
"""

USAGE = "%(prog)s [-h] -- cmd [cmd ...]"

EPILOG = """
Insert this command before the one you usually use to start your webserver
to apply Contrast's instrumentation. See our public documentation for details:
https://docs.contrastsecurity.com/en/python.html
"""


def runner() -> None:
    logger.info("Starting Contrast Agent runner pre-process")
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        usage=USAGE,
        epilog=EPILOG,
    )
    parser.add_argument(
        "--rewrite-for-pytest", action="store_true", help=argparse.SUPPRESS
    )
    # if you add public arguments here, update USAGE accordingly
    parser.add_argument(
        "cmd",
        nargs="+",
        help="Command to run with the agent. cmd should be available in the operating system PATH.",
    )

    parsed = parser.parse_args()

    config = AgentConfig()

    loader_path = os.path.join(os.path.dirname(__file__), "loader")
    os.environ["PYTHONPATH"] = os.path.pathsep.join([loader_path] + sys.path)
    os.environ["CONTRAST_INSTALLATION_TOOL"] = "CONTRAST_PYTHON_RUN"

    if parsed.rewrite_for_pytest or config.should_pytest_rewrite:
        os.environ[REWRITE_FOR_PYTEST] = "true"

    cmd_path, *args = shutil.which(parsed.cmd[0]), *parsed.cmd
    if cmd_path is None:
        logger.error("Command not found in PATH", cmd=parsed.cmd[0])
        logger.info(f"Run '{sys.argv[0]} --help' for usage information.")
        sys.exit(1)
        return
    os.execl(cmd_path, *args)
