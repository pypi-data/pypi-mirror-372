import pytest

from shouldersurfscore.classes.bounds import Bounds
from shouldersurfscore.classes.point import Point


def test_creation():
    with pytest.raises(ValueError):
        bounds = Bounds(0, 10, -10, 0)
    with pytest.raises(ValueError):
        bounds = Bounds(0, -10, 10, 0)
    bounds = Bounds(0, 10, 10, 0)
    assert bounds.top_left == Point(0, 10)
    assert bounds.top_right == Point(10, 10)
    assert bounds.bottom_left == Point(0, 0)
    assert bounds.bottom_right == Point(10, 0)


def test_from_points():
    points = [Point(0, 0), Point(-11, 100), Point(3, -25)]
    bounds = Bounds.from_points(points)
    assert bounds.left == -11
    assert bounds.right == 3
    assert bounds.top == 100
    assert bounds.bottom == -25


def test_contains():
    bounds = Bounds(-10, 10, 10, -10)
    assert bounds.contains(Point(0, 0))
    assert bounds.contains(Point(-10, 3.214))
    assert bounds.contains(Point(-7.8, -3.214))
    assert not bounds.contains(Point(100, 0))
    assert not bounds.contains(Point(100, 100))
    assert not bounds.contains(Point(0, 100))


def test_shifted_by():
    # unit square bounds
    bounds = Bounds(-1, 1, 1, -1)
    point = Point(5, 5)
    # Should shift the box to be centered on (5,by
    bounds = bounds.shifted_by(point)
    assert bounds.bottom == 4
    assert bounds.left == 4
    assert bounds.top == 6
    assert bounds.right == 6
