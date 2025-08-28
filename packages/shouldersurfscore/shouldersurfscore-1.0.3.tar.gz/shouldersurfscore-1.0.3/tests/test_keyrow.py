import pytest

from shouldersurfscore.classes.key import Key
from shouldersurfscore.classes.keyrow import KeyRow
from shouldersurfscore.classes.point import Point


def test_from_characters():
    chars = "asdf"
    row = KeyRow.from_characters(chars)
    i = 0
    for ch, key in zip(chars, row):
        assert key.value == ch
        assert key.shift_value == ch.upper()
        assert key.position == Point(i, 0)
        i += 1


def test_from_character_pairs():
    chars = "1!2@3#4$5%"
    with pytest.raises(ValueError):
        KeyRow.from_character_pairs(chars[1:])
    row = KeyRow.from_character_pairs(chars)
    assert len(row) == (len(chars) / 2)

    assert row[0].value == "1"
    assert row[0].shift_value == "!"
    assert row[-1].value == "5"
    assert row[-1].shift_value == "%"

    for i, key in enumerate(row):
        assert key.value == chars[2 * i]
        assert key.shift_value == chars[(2 * i) + 1]


def test_iteration():
    chars = "qwertyuiop"
    row = KeyRow.from_characters(chars)
    # __len__
    assert len(row) == len(chars)
    # __getitem__
    assert row[0].value == chars[0]
    # __iter__ and __next__
    for key, ch in zip(row, chars):
        assert key.value == ch


def test_append():
    row = KeyRow.from_characters("asdf")
    # Setting a position to make sure it gets overwritten
    # should be (len(row) - 1, 0)
    row.append(Key("g", position=Point(10, 10)))
    assert row[-1].position == Point(len(row) - 1, 0)


def test_extend():
    row = KeyRow.from_characters("asd")
    assert len(row) == 3
    row.extend(KeyRow.from_characters("fg"))
    assert len(row) == 5
    assert row[-2].value == "f"
    assert row[-1].value == "g"


def test_add():
    row = KeyRow.from_characters("as") + KeyRow.from_characters("df")
    assert len(row) == 4
    for i, ch in enumerate("asdf"):
        assert row[i].value == ch
    row += KeyRow.from_characters("gh")
    assert len(row) == 6
    for i, ch in enumerate("asdfgh"):
        assert row[i].value == ch


def test_str():
    row = KeyRow.from_characters("asdf")
    assert str(row) == "aA sS dD fF"
    row = KeyRow.from_characters("1234")
    assert str(row) == "1 2 3 4"
