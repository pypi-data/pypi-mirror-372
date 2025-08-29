# ----------------------------------------------------------------------
# Gufo Liftbridge: gufo.liftbridge.compressor tests
# ----------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Liftbridge modules
from gufo.liftbridge.compressor import _get_handlers, compress, decompress


def test_get_handlers_invalid_method():
    with pytest.raises(ValueError):
        _get_handlers("invalid")


def test_get_handlers_zlib_fn():
    comp, decomp = _get_handlers("zlib")
    from zlib import compress, decompress

    assert comp is compress
    assert decomp is decompress


def test_get_handlers_lzma_fn():
    comp, decomp = _get_handlers("lzma")
    from lzma import compress, decompress

    assert comp is compress
    assert decomp is decompress


@pytest.mark.parametrize("method", ["zlib", "lzma"])
def test_get_handlers_cycle(method: str):
    comp, decomp = _get_handlers(method)
    assert comp is not decomp
    sample = b"a" * 1024
    # Compress
    cdata = comp(sample)
    # Compressed value must differ
    assert isinstance(cdata, bytes)
    assert len(cdata) < len(sample)
    assert cdata != sample
    # Decompress
    data = decomp(cdata)
    assert isinstance(data, bytes)
    assert data == sample


@pytest.mark.parametrize("method", ["zlib", "lzma"])
def test_get_cycle(method: str):
    sample = b"a" * 1024
    for _ in range(2):
        # Compress
        cdata = compress(sample, method)
        # Compressed value must differ
        assert isinstance(cdata, bytes)
        assert len(cdata) < len(sample)
        assert cdata != sample
        # Decompress
        data = decompress(cdata, method)
        assert isinstance(data, bytes)
        assert data == sample
