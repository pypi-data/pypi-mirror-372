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

from typing import Any


def sanitize_keys(data: Any) -> Any:
    """
    Recursively convert all keys in a dictionary or list to strings.
    This is useful for ensuring that all keys are of a consistent type,
    especially when dealing with JSON-like structures and Protobuf Structs.

    Parameters
    ----------
    data : Any
        The input data, which can be a dictionary, list, or any other type.
    Returns
    -------
    Any
        The input data with all dictionary keys converted to strings.
    """
    if isinstance(data, dict):
        return {str(key): sanitize_keys(value) for key, value in data.items()}
    if isinstance(data, list):
        return [sanitize_keys(item) for item in data]
    return data


def convert_tuples_to_lists(data: Any) -> Any:
    """
    Recursively converts tuples in a dictionary to lists.

    This is useful for ensuring that all data structures are of a consistent type,
    especially when dealing with JSON-like structures and Protobuf Structs.

    Parameters
    ----------
    data : Any
        The input data, which can be a dictionary, list, or any other type.

    Returns
    -------
    Any
        The input data with all tuples converted to lists.
    """
    if isinstance(data, dict):
        return {key: convert_tuples_to_lists(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_tuples_to_lists(item) for item in data]
    if isinstance(data, tuple):
        return list(data)
    return data
