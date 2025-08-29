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
Classes for representing and manipulating Pauli operators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Optional,
    Union,
    get_args,
)

import numpy as np

from qctrlcommons.exceptions import QctrlArgumentsValueError

VALID_PAULI_STRINGS = frozenset({"I", "X", "Y", "Z"})

ComplexLike = Union[int, float, complex]


@dataclass
class PauliOperator:
    """
    Class representing a sparse Pauli operator.

    Parameters
    ----------
    paulis : str or list[str]
        The string representation of a Pauli operator or a list of Pauli operator strings.
    coefficients : ComplexLike or list[ComplexLike] or np.ndarray or None, optional
        Coefficients for the Pauli operators. If not provided, the coefficients default to 1.0
        for each operator.
    """

    paulis: str | list[str]
    coefficients: Optional[ComplexLike | list[ComplexLike] | np.ndarray] = None

    def __post_init__(self):
        if not isinstance(self.paulis, list):
            self.paulis = [self.paulis]

        assert all(
            isinstance(pauli, str)
            and all(char.upper() in VALID_PAULI_STRINGS for char in pauli)
            for pauli in self.paulis
        ), f"Pauli strings must be strings containing only {list(VALID_PAULI_STRINGS)}"

        if self.coefficients is None:
            self.coefficients = np.ones(len(self.paulis), dtype=complex)
        elif isinstance(self.coefficients, get_args(ComplexLike)):
            self.coefficients = np.asarray([self.coefficients], dtype=complex)
        else:
            self.coefficients = np.asarray(self.coefficients, dtype=complex)

        assert (
            len(self.paulis) == self.coefficients.size
        ), "Length of paulis and coefficients must match."

    def __str__(self):
        return str(self.to_dict())

    def __eq__(self, value: PauliOperator):
        if not isinstance(value, PauliOperator):
            raise TypeError("other must be a PauliOperator")
        return (
            np.allclose(self.coefficients, value.coefficients)
            and self.paulis == value.paulis
        )

    def to_dict(self) -> dict:
        """
        Convert the Pauli operator to a dictionary representation.

        Returns
        -------
        dict[str, complex]
            Dictionary representation of the Pauli operator.
        """
        return dict(zip(self.paulis, self.coefficients))

    @staticmethod
    def from_dict(pauli_dict: dict, dtype: type = complex) -> "PauliOperator":
        """
        Construct from a dictionary containing Pauli strings and coefficients.

        Parameters
        ----------
        pauli_dict : dict[str, complex]
            A dictionary specifying the Pauli terms.
        dtype : type, optional
            The data type to be used for storing the coefficients. Defaults to `complex`.

        Returns
        -------
        PauliOperator
            The constructed Pauli operator.
        """
        return PauliOperator.from_list(list(pauli_dict.items()), dtype=dtype)

    def to_list(self) -> list[tuple[str, complex]]:
        """
        Convert the Pauli operator to a list of tuples.

        Returns
        -------
        list[tuple[str, complex]]
            List of tuples containing the Pauli strings and coefficients.
        """
        return list(zip(self.paulis, self.coefficients))

    @staticmethod
    def from_list(
        pauli_tuples: list[tuple[str, complex]],
        dtype: type = complex,
        qubit_count: Optional[int] = None,
    ) -> "PauliOperator":
        """
        Construct from a list of tuples containing Pauli strings and coefficients.

        Parameters
        ----------
        pauli_tuples : list[tuple[str, complex]]
            A list of tuples specifying the Pauli terms.
        qubit_count : Optional[int], optional
            The number of qubits in the system. If not provided, it will be inferred automatically
            from the length of the Pauli strings inside `pauli_tuples`.
        dtype : type, optional
            The data type to be used for storing the coefficients. Defaults to `complex`.

        Returns
        -------
        PauliOperator
            The constructed Pauli operator.

        Raises
        ------
        QctrlArgumentsValueError
            If the `qubit_count` is smaller than the length of any Pauli string in `pauli_tuples`.
        """
        pauli_tuples = list(pauli_tuples)  # To convert zip or other iterable
        size = len(pauli_tuples)

        if qubit_count is None:
            if size == 0:
                raise QctrlArgumentsValueError(
                    "Could not determine the number of qubits from empty `pauli_tuples`. "
                    "Try passing `qubit_count`.",
                    {
                        "pauli_tuples": pauli_tuples,
                    },
                )
            pauli_lengths = [len(pauli_tuple[0]) for pauli_tuple in pauli_tuples]
            if not all(length == pauli_lengths[0] for length in pauli_lengths):
                raise QctrlArgumentsValueError(
                    "Pauli strings in `pauli_tuples` must all be the same qubit length.",
                    {
                        "pauli_tuples": pauli_tuples,
                    },
                )
            qubit_count = pauli_lengths[0]
        else:
            for pauli_tuple in pauli_tuples:
                if len(pauli_tuple[0]) != qubit_count:
                    raise QctrlArgumentsValueError(
                        f"The length of Pauli string '{pauli_tuple[0]}' doesn't match the "
                        "passed in number of qubits.",
                        {
                            "qubit_count": qubit_count,
                        },
                    )

        if size == 0:
            pauli_tuples = [("I" * qubit_count, 0)]
            size = len(pauli_tuples)

        coeffs = np.zeros(size, dtype=dtype)
        labels = np.zeros(size, dtype=f"<U{qubit_count}")
        for index, item in enumerate(pauli_tuples):
            labels[index] = item[0]
            coeffs[index] = item[1]

        return PauliOperator(list(labels), coeffs)

    @staticmethod
    def from_sparse_list(
        sparse_list: list[tuple[str, list[int], complex]],
        qubit_count: int,
        dtype: type = complex,
    ) -> "PauliOperator":
        """
        Construct from a list of local Pauli strings and coefficients.

        Parameters
        ----------
        sparse_list : list[tuple[str, list[int], complex]]
            List of tuples containing the Pauli string, indices of non-trivial Paulis, and
            coefficients.
        qubit_count : int
            Number of qubits in the system.
        dtype : type, optional
            Data type for the coefficients. Defaults to `complex`.

        Returns
        -------
        PauliOperator
            The constructed Pauli operator.

        Raises
        ------
        QctrlArgumentsValueError
            If the input indices are duplicated or if the `qubit_count` is smaller than a
            given Pauli index.
        """
        sparse_list = list(sparse_list)  # To convert zip or other iterable
        size = len(sparse_list)

        if size == 0:
            sparse_list = [("I" * qubit_count, range(qubit_count), 0)]
            size = len(sparse_list)

        coeffs = np.zeros(size, dtype=dtype)
        labels = np.zeros(size, dtype=f"<U{qubit_count}")

        for i, (paulis, indices, coeff) in enumerate(sparse_list):
            if len(indices) != len(set(indices)):
                raise QctrlArgumentsValueError(
                    "Input indices are duplicated.",
                    {
                        "indices": indices,
                    },
                )
            # construct the full label based off the non-trivial Paulis and indices
            label = ["I"] * qubit_count
            for pauli, index in zip(paulis, indices):
                if index >= qubit_count:
                    raise QctrlArgumentsValueError(
                        f"The number of qubits is smaller than a required index {index}.",
                        {
                            "qubit_count": qubit_count,
                        },
                    )
                label[~index] = pauli

            labels[i] = "".join(label)
            coeffs[i] = coeff

        return PauliOperator(list(labels), coeffs)
