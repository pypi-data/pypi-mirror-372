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
"""Dataclasses defining options for Fire Opal circuit execution."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RunOptions:
    """
    Provider-agnostic options for Fire Opal circuit execution.
    """


@dataclass
class IbmRunOptions(RunOptions):
    """
    Options for circuit execution on IBM devices through Fire Opal.

    Parameters
    ----------
    session_id: str or None, optional
        The ID of an IBM Runtime session to use for circuit execution.
        Defaults to None.
    job_tags: list of str or None, optional
        The list of tags to append to the jobs submitted to IBM.
        Defaults to None.
    """

    session_id: Optional[str] = None
    job_tags: Optional[list[str]] = None
