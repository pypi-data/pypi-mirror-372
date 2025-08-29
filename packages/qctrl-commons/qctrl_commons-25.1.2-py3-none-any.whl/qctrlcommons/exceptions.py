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
Module for handling exceptions.
"""

from typing import (
    Any,
    Dict,
    Optional,
)


class QctrlException(Exception):
    """
    Base class for all qctrl-related errors.
    """


class QctrlGraphIntegrityError(QctrlException):
    """
    Specialized exception which will be raised to handle `Graph` related errors.
    """


class QctrlArgumentsValueError(QctrlException, ValueError):
    """
    Exception thrown when one or more arguments provided to a method have incorrect values.

    Parameters
    ----------
    description : str
        Description of why the input error occurred.
    arguments : dict
        Dictionary containing the arguments of the method that contributed to the error.
    extras : dict
        Optional. Other variables that contributed to the error but are not arguments of the method.
    """

    def __init__(
        self, description: str, arguments: dict, extras: Optional[dict] = None
    ):
        message = description
        for key in arguments:
            message += f"\n{str(key)}={repr(arguments[key])}"
        if extras:
            for key in extras:
                message += f"\n{str(key)}={repr(extras[key])}"
        super().__init__(message)


class QctrlUserInputError(QctrlException, ValueError):
    """
    Exception for representing incorrect input from the user.

    Parameters
    ----------
    description : str
        The message explaining the incorrect input.
    arguments : dict[str, Any]
        Arguments that contributed to the error.
    extras : dict, optional
        Other variables that contributed to the error but are not arguments of the method.
        Defaults to None.
    """

    def __init__(
        self, description: str, arguments: Dict[str, Any], extras: Optional[dict] = None
    ) -> None:
        error_message = description
        for extra in [arguments, extras]:
            if extra:
                extra_str = ", ".join(f"{key}={value}" for key, value in extra.items())
                error_message += f"; {extra_str}"

        super().__init__(error_message)
