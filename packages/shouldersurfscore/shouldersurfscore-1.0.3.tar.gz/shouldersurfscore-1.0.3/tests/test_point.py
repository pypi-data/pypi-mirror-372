import pytest

from shouldersurfscore.classes.point import Point


def test_equality():
    p1 = Point(0, 0)
    p2 = Point(0, 0)
    assert p1 == p2
    p2.x = 1
    assert p1 != p2
    with pytest.raises(TypeError):
        assert p1 == "yeehaw"


def test_str():
    p1 = Point(11, 22)
    assert str(p1) == "(11, 22)"


def test_subtraction():
    p1 = Point(1, 1)
    assert Point(0, 0) == (p1 - p1)
    p2 = Point(2, 3)
    assert (p2 - p1) == Point(1, 2)
    assert (p1 - p2) == Point(-1, -2)
    p2 -= p1
    assert p2 == Point(1, 2)
    p1 -= p1
    assert p1 == Point(0, 0)


def test_addition():
    p1 = Point(1, 1)
    assert p1 + p1 == Point(2, 2)
    p2 = Point(-2, 2)
    assert (p1 + p2) == Point(-1, 3)
    assert (p2 + p1) == Point(-1, 3)
    p2 += p1
    assert p2 == Point(-1, 3)
    p1 += p1
    assert p1 == Point(2, 2)


def test_distance():
    p1 = Point(1, 1)
    p2 = Point(5, 1)
    assert p1.distance(p2) == 4
    assert p2.distance(p1) == 4
    # 3-4-5 triangle
    p1 = Point(0, 0)
    p2 = Point(3, 4)
    assert p1.distance(p2) == 5
    assert p2.distance(p1) == 5


def test_vector():
    # 3-4-5 triangle offset by 1
    p1 = Point(1, y=1)
    assert p1.vector(p1) == Point(0, 0)
    p2 = Point(4, 5)
    # should be how to get from `p1` to `p2`
    v = p1.vector(p2)
    assert v == Point(3, 4)


def test_as_tuple():
    p = Point(-10, 200)
    t = p.as_tuple()
    assert t[0] == p.x
    assert t[1] == p.y
    assert t == (-10, 200)
