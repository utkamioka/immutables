from __future__ import annotations

__all__ = ['immutable', 'mutable']

from collections.abc import Mapping, Sequence, Callable, Iterable
from types import MappingProxyType
from typing import Any


class _Translator:
    def __init__(self,
                 *,
                 mapping: Callable[[Mapping], Mapping],
                 sequence: Callable[[Sequence | Iterable], Sequence],
                 iterable: Callable[[Iterable], Iterable]):
        self._mapping = mapping
        self._sequence = sequence
        self._iterable = iterable

    def translate(self, obj: Any) -> Any:
        if isinstance(obj, Mapping):
            return self._mapping({k: self.translate(v) for k, v in obj.items()})
        if isinstance(obj, Sequence) and not isinstance(obj, str):
            return self._sequence(self.translate(v) for v in obj)
        if isinstance(obj, Iterable) and not isinstance(obj, str):
            return self._iterable(self.translate(v) for v in obj)
        return obj


def immutable(obj: Any,
              *,
              mapping: Callable[[Mapping], Mapping] = MappingProxyType,
              sequence: Callable[[Sequence | Iterable], Sequence] = tuple,
              iterable: Callable[[Iterable], Iterable] = frozenset) -> Any:
    return _Translator(mapping=mapping, sequence=sequence, iterable=iterable).translate(obj)


def mutable(obj: Any,
            *,
            mapping: Callable[[Mapping], Mapping] = dict,
            sequence: Callable[[Sequence | Iterable], Sequence] = list,
            iterable: Callable[[Iterable], Iterable] = set) -> Any:
    return _Translator(mapping=mapping, sequence=sequence, iterable=iterable).translate(obj)
