"""Library to interact with the Biwenger API."""

import os
import typing as t

from pybiwenger.src.biwenger.league import League
from pybiwenger.src.biwenger.market import Market
from pybiwenger.src.biwenger.players import Players
from pybiwenger.src.client.client import BiwengerBaseClient
from pybiwenger.utils.log import PabLog

lg = PabLog(__name__)


def authenticate(
    username: t.Optional[str] = None, password: t.Optional[str] = None
) -> None:
    if not username or not password:
        if os.getenv("BIWENGER_USERNAME") and os.getenv("BIWENGER_PASSWORD"):
            lg.log.info("Using existing environment variables for authentication.")
            return
    """Create a Biwenger client instance and log in."""
    os.environ["BIWENGER_USERNAME"] = username
    os.environ["BIWENGER_PASSWORD"] = password
    lg.log.info("Authentication details set in environment variables.")
