from shouldersurfscore.classes.key import Key
from shouldersurfscore.classes.point import Point


def test_Key_values():
    key = Key("a")
    assert key.value == "a"
    assert key.shift_value == "A"
    key = Key("a", "4")
    assert key.shift_value == "4"
    key = Key("3")
    assert key.shift_value is None


def test_Key_distance():
    # 3-4-5 triangle
    k1 = Key("a", position=Point(0, 0))
    k2 = Key("r", position=Point(3, 4))
    assert k1.distance(k2) == 5
    assert k2.distance(k1) == 5


def test_Key_vector():
    # 3-4-5 triangle offset by 1
    k1 = Key("a", position=Point(1, y=1))
    assert k1.vector(k1) == Point(0, 0)
    k2 = Key("r", position=Point(4, y=5))
    assert k1.vector(k2) == Point(3, 4)


def test_Key_str():
    key = Key("a")
    assert str(key) == "aA"
    key = Key("1")
    assert str(key) == "1"
    key = Key("1", "!")
    assert str(key) == "1!"
