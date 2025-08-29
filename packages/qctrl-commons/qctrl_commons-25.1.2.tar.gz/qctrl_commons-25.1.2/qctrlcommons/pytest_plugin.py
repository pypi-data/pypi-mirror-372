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

import inspect
from abc import (
    ABC,
    abstractmethod,
)
from collections import namedtuple
from datetime import datetime
from typing import Type

import pytest
from graphql import DocumentNode

# pylint:disable=too-few-public-methods


@pytest.fixture(scope="session")
def mock_types():
    """Provides type checking for mock.assert_called_with args."""

    class TypeCheck(ABC):
        """Base type checking class for when exact values
        are not known when calling mock.assert_called_with.

        e.g.
        mock.assert_called_with(pid=mock_types.int())
        """

        @abstractmethod
        def _is_valid(self, value) -> bool:
            """Checks if the value is valid."""
            raise NotImplementedError

        def __eq__(self, value):
            return self._is_valid(value)

        def __ne__(self, value):
            return not self._is_valid(value)

    class SimpleTypeCheck(TypeCheck):
        """Simple type checking using `isinstance`."""

        _type: Type = None

        def _is_valid(self, value):
            if self._type is None:
                raise ValueError("`_type` not set")

            if not inspect.isclass(self._type):
                raise ValueError("`_type` is not a class")

            return (
                isinstance(  # pylint:disable=isinstance-second-argument-not-valid-type
                    value, self._type
                )
            )

    class Int(SimpleTypeCheck):
        """Integer type checker."""

        _type = int

    class DateTime(SimpleTypeCheck):
        """DateTime type checker."""

        _type = datetime

    class GraphQLDocument(SimpleTypeCheck):
        """GraphQL DocumentNode type checker."""

        _type = DocumentNode

    cls = namedtuple("MockTypes", ["int", "datetime", "graphql_document"])
    return cls(int=Int, datetime=DateTime, graphql_document=GraphQLDocument)
