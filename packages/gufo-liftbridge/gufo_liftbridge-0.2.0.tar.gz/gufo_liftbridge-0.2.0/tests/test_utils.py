# ----------------------------------------------------------------------
# Gufo Liftbridge: gufo.liftbridge.utils tests
# ----------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Liftbridge modules
from gufo.liftbridge.utils import is_ipv4


@pytest.mark.parametrize(
    ("v", "exp"),
    [
        ("192.168.0.1", True),
        ("192.168.0", False),
        ("192.168.0.1.1", False),
        ("192.168.1.256", False),
        ("192.168.a.250", False),
        ("11.24.0.09", False),
    ],
)
def test_is_ip(v: str, exp: bool) -> None:
    assert is_ipv4(v) is exp
