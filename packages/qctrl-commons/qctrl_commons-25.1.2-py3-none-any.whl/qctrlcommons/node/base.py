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
Module for Node.
"""

from __future__ import annotations


class Node:  # pylint: disable=too-few-public-methods
    """
    An operation in a computational graph is represented by a Node.
    This class defines its ID and dependencies.

    Parameters
    ----------
    node_id : str
        Graph node identity (user-specified name of the node).
    input_kwargs : Dict
        Dictionary of inputs passed to the graph node.
    """

    def __init__(self, node_id: str, input_kwargs: dict):
        self.node_id = node_id
        self.input_kwargs = input_kwargs
