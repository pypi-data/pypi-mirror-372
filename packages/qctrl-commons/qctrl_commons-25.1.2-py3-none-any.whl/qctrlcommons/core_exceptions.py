# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Exceptions raised in Core packages.
"""

from __future__ import annotations

from enum import Enum
from functools import partial
from typing import (
    Any,
    Optional,
    Type,
)


class QctrlCoreError(Exception):
    """
    Exception raised in a Core package.

    Parameters
    ----------
    message : str
        Description of why the error occurred.
    arguments : dict or None, optional
        Optional dictionary containing variables that contributed to the error.
    """

    def __init__(self, message: str, extras: Optional[dict] = None):
        if extras is not None:
            _extra = ", ".join([f"{key}={repr(val)}" for key, val in extras.items()])
            message = f"{message} {_extra}"
        super().__init__(message)


class QctrlCorePublicError(QctrlCoreError):
    """
    Core exception that should be re-raised to users.
    """


class QctrlCoreInternalError(QctrlCoreError):
    """
    Core exception that shouldn't be re-raised to users.
    """


class QctrlCoreHardwareProviderError(QctrlCoreError):
    """
    Core exception that should be used to raise provider errors to users.
    """


def _check_argument(
    condition: Any,
    description: str,
    extras: Optional[dict] = None,
    *,
    exception: Type[QctrlCoreError],
) -> None:
    """
    If the condition is false, raise the exception with the specified parameters.
    """
    if condition:
        return
    raise exception(description, extras)


class CoreValidator(Enum):
    """
    Validators for raising exceptions.
    """

    INTERNAL = partial(_check_argument, exception=QctrlCoreInternalError)
    PUBLIC = partial(_check_argument, exception=QctrlCorePublicError)

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)
