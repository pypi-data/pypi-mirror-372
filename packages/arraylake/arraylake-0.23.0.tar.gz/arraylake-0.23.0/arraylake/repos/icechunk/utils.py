from __future__ import annotations

import importlib


def _raise_if_no_icechunk():
    """Check if icechunk is available in the environment and raise an error if it is not.

    Icechunk is required to interact with a V2 repo.
    """
    if not importlib.util.find_spec("icechunk"):
        raise ImportError("Icechunk not found in the environment! Icechunk repos are not supported.")
