import pytest

from stix_traverser import EmptyTraverser

def test_empty_traverser():

    traverser = EmptyTraverser()
    assert traverser.a == traverser
    assert traverser.a.b == traverser
    assert traverser.a.b.c == traverser

    assert traverser() is None
    assert traverser.a() is None

    assert not traverser
    assert not traverser()
    assert not traverser.a()

    assert not traverser[0]
    assert not traverser[0][2]
    assert not traverser[0]()
    assert not traverser[0].a
    assert not traverser[0].a()

    if traverser.a.b:
        pytest.fail("Empty traverser must act as False")