# ----------------------------------------------------------------------
# Liftbridge errors
# ----------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ----------------------------------------------------------------------
"""Errors definitions."""

# Python modules
from types import TracebackType
from typing import Dict, Type

# Third-party modules
from grpc import StatusCode  # type:ignore[import-untyped]
from grpc.experimental.aio import AioRpcError  # type:ignore[import-untyped]


class LiftbridgeError(Exception):
    """Base class for LirtBridgeClient errors."""


class ErrorNotFound(LiftbridgeError):
    """Unable to resolve broker."""


class ErrorAlreadyExists(LiftbridgeError):
    """Partition is already exists."""


class ErrorChannelClosed(LiftbridgeError):
    """Channel is terminated by broker."""


class ErrorUnavailable(LiftbridgeError):
    """Broker is not available."""


class ErrorMessageSizeExceeded(LiftbridgeError):
    """Message size exceeds allowed limit."""


class ErrorNoMetadataLeader(LiftbridgeError):
    """No known metadata leader."""


RPC_CODE_TO_ERR: Dict[StatusCode, Type[LiftbridgeError]] = {
    StatusCode.ALREADY_EXISTS: ErrorAlreadyExists,
    StatusCode.NOT_FOUND: ErrorNotFound,
    StatusCode.UNAVAILABLE: ErrorUnavailable,
    StatusCode.RESOURCE_EXHAUSTED: ErrorMessageSizeExceeded,
}


class rpc_error(object):
    """Context manager to process RPC errors."""

    def __init__(self) -> None:
        pass

    def __enter__(self) -> None:
        """Enter context."""

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        """Exit context handler."""
        if exc_val and isinstance(exc_val, AioRpcError):
            code = exc_val.code()
            details = exc_val.details()
            if is_no_metada_leader(exc_val):
                raise ErrorNoMetadataLeader
            xcls = RPC_CODE_TO_ERR.get(code) or LiftbridgeError
            raise xcls(details)


def is_no_metada_leader(exc: AioRpcError) -> bool:
    """Check if the error is `no known metadata leader`."""
    code = exc.code()
    details = exc.details()
    return (
        code == StatusCode.INTERNAL
        and details is not None
        and details == "no known metadata leader"
    )
