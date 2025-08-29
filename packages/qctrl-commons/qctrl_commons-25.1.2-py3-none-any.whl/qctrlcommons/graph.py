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
import logging
from typing import (
    Any,
    Dict,
)

LOGGER = logging.getLogger(__name__)


class Graph:
    """
    A class for representing and building a Boulder Opal data flow graph.

    The graph object is the main entry point to the Boulder Opal graph ecosystem.
    You can call methods to add nodes to the graph, and use the `operations` attribute to get a
    dictionary representation of the graph.
    """

    def __init__(self):
        self.operations = {}

    def __getattr__(self, attr):
        # We override getattr to stop pylint from complaining about missing attributes for methods
        # that are added dynamically.
        raise AttributeError(f"'Graph' object has no attribute '{attr}'.")

    @classmethod
    def _from_operations(cls, operations: Dict[str, Any]):
        """
        Create a new graph from an existing set of operations.

        Parameters
        ----------
        operations : dict[str, Any]
            The initial dictionary of operations for the graph.
        """
        graph = cls()
        graph.operations = operations
        return graph
