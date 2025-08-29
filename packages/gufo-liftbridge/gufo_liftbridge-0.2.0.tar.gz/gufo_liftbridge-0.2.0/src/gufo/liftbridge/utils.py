# ----------------------------------------------------------------------
# Gufo Liftbridge: Various utilities.
# ----------------------------------------------------------------------
# Copyright (C) 2022-2025, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------
"""Various utilities."""

# Python modules
import socket

IP_PARTS = 4
MAX_OCTET = 0xFF


def is_ipv4(addr: str) -> bool:
    """
    Check value is valid IPv4 address.

    Args:
        addr: String to check.

    Returns:
        `True`, if is valid IPv4 address. `False` otherwise.
    """
    parts = addr.split(".")
    if len(parts) != IP_PARTS:
        return False
    try:
        return all(0 <= int(x) <= MAX_OCTET for x in parts) and bool(
            socket.inet_aton(addr)
        )
    except (ValueError, OSError):
        return False
