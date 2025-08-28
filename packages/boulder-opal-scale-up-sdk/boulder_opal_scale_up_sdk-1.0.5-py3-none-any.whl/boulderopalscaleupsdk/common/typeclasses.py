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

from abc import abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import Any, Protocol, TypeVar, overload

T = TypeVar("T")


class Combine(Protocol[T]):
    """The combine typeclass defines the behaviour when types are combined."""

    @abstractmethod
    def combine(self, first: T, second: T) -> T: ...

    @overload
    def combine_option(self, first: T, second: T | None) -> T: ...

    @overload
    def combine_option(self, first: T | None, second: T) -> T: ...

    @overload
    def combine_option(self, first: None, second: None) -> None: ...

    def combine_option(self, first: T | None, second: T | None) -> T | None:
        return Combine[T].option(self).combine(first, second)

    @classmethod
    def create(cls, combine_fn: Callable[[T, T], T]) -> "Combine[T]":
        class _Combine(Combine):
            def combine(self, first: T, second: T) -> T:
                return combine_fn(first, second)

        return _Combine()

    @classmethod
    def replace(cls) -> "Combine[T]":
        def _combine(_first: T, second: T) -> T:
            return second

        return Combine[T].create(_combine)

    @classmethod
    def option(cls, combine: "Combine[T]") -> "Combine[T | None]":
        def _combine(first: T | None, second: T | None) -> T | None:
            match first, second:
                case None, None:
                    return None
                case first, None:
                    return first
                case None, second:
                    return second
                case _:
                    return combine.combine(first, second)  # type: ignore[arg-type]

        return Combine.create(_combine)

    @staticmethod
    def deep_merge(combine_value: "Combine[Any]") -> "Combine[dict[Any, Any]]":
        def _combine_inplace_recursively(source: dict[Any, Any], dest: dict[Any, Any]):
            for key, value in source.items():
                if isinstance(value, dict):
                    node = dest.setdefault(key, {})
                    _combine_inplace_recursively(value, node)
                else:
                    dest[key] = Combine.option(combine_value).combine(dest.get(key), value)

        def _combine(first: dict[Any, Any], second: dict[Any, Any]) -> dict[Any, Any]:
            destination = deepcopy(first)
            _combine_inplace_recursively(source=second, dest=destination)
            return destination

        return Combine.create(_combine)


class Eq(Protocol[T]):
    @abstractmethod
    def eq(self, first: T, second: T) -> bool: ...

    def eq_option(self, first: T | None, second: T | None) -> bool:
        match first, second:
            case None, None:
                return True
            case _ if first is not None and second is not None:
                return self.eq(first, second)
            case _:
                return False

    @classmethod
    def create(cls, eq_fn: Callable[[T, T], bool]) -> "Eq[T]":
        class _Eq(Eq):
            def eq(self, first: T, second: T) -> bool:
                return eq_fn(first, second)

        return _Eq()
