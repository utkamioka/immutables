import os
import subprocess
from collections import defaultdict
from types import MappingProxyType

from _pytest.monkeypatch import MonkeyPatch

from immutables import immutable


def test_immutable():
    obj1 = {
        # dict includes mapping, sequence, iterable and other
        'a': {'a': {'foo': 'bar'}, 'b': [1, 2], 'c': set('xyz'), 'd': 'xyz'},
        # list includes mapping, sequence, iterable and other
        'b': [{'b': 'bravo'}, range(3), set('xyz'), 'xyz'],
        # tuple includes sequence, iterable and other
        'c': {(1, 2, 3), frozenset(set('xyz')), 'xyz'},
    }
    obj2 = immutable(obj1)

    assert isinstance(obj2, MappingProxyType)

    assert isinstance(obj2['a'], MappingProxyType)
    assert isinstance(obj2['a']['a'], MappingProxyType)
    assert isinstance(obj2['a']['b'], tuple)
    assert isinstance(obj2['a']['c'], frozenset)
    assert obj2['a'] == dict(a=dict(foo='bar'), b=(1, 2), c={'x', 'y', 'z'}, d='xyz')

    assert isinstance(obj2['b'], tuple)
    assert isinstance(obj2['b'][0], MappingProxyType)
    assert isinstance(obj2['b'][1], tuple)
    assert isinstance(obj2['b'][2], frozenset)
    assert obj2['b'] == (dict(b='bravo'), (0, 1, 2), {'x', 'y', 'z'}, 'xyz')

    assert isinstance(obj2['c'], frozenset)
    it = iter(obj2['c'])
    o = next(it)
    assert isinstance(o, tuple)
    assert o == (1, 2, 3)
    o = next(it)
    assert isinstance(o, frozenset)
    assert o == {'x', 'y', 'z'}
    o = next(it)
    assert o == 'xyz'


def test_immutable__with_mapping(monkeypatch: MonkeyPatch):
    for name in os.environ.keys():
        monkeypatch.delenv(name)
    monkeypatch.setenv('D', 'delta')

    # Python標準のMappingな（dictライクな）オブジェクト
    obj1 = [
        dict(A='alpha'),
        defaultdict(str, dict(B='bravo')),
        MappingProxyType(dict(C='charlie')),
        os.environ,
    ]
    obj2 = immutable(obj1)

    assert isinstance(obj2[0], MappingProxyType)
    assert isinstance(obj2[1], MappingProxyType)
    assert isinstance(obj2[2], MappingProxyType)
    assert isinstance(obj2[3], MappingProxyType)
    assert obj2[0] == {'A': 'alpha'}
    assert obj2[1] == {'B': 'bravo'}
    assert obj2[2] == {'C': 'charlie'}
    assert obj2[3] == {'D': 'delta'}


def test_immutable__with_sequence():
    obj1 = [
        list([1]),
        tuple([2]),
        range(3),
    ]
    obj2 = immutable(obj1)

    assert isinstance(obj2[0], tuple)
    assert isinstance(obj2[1], tuple)
    assert isinstance(obj2[2], tuple)
    assert obj2[0] == (1,)
    assert obj2[1] == (2,)
    assert obj2[2] == (0, 1, 2)


def test_immutable__with_iterable():
    obj1 = [
        {1, 2, 3},
        dict(a=1, b=2, c=3).keys(),
    ]
    obj2 = immutable(obj1)

    assert isinstance(obj2[0], frozenset)
    assert isinstance(obj2[1], frozenset)
    assert obj2[0] == {1, 2, 3}
    assert obj2[1] == {'a', 'b', 'c'}
