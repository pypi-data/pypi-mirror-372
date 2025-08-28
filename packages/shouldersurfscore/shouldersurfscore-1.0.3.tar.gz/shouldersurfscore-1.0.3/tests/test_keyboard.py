from collections.abc import Callable
from typing import Any

import pytest
from matplotlib.figure import Figure
from rich.prompt import Confirm

from shouldersurfscore.classes.bounds import Bounds
from shouldersurfscore.classes.key import Key
from shouldersurfscore.classes.keyboard import Keyboard
from shouldersurfscore.classes.keyplotter import KeyPlotter, KeyStyle
from shouldersurfscore.classes.keyrow import KeyRow
from shouldersurfscore.classes.point import Point


def get_test_keyboard(
    offsets: tuple[float, float, float, float] = (0, 0, 0, 0)
) -> Keyboard:
    r0 = KeyRow.from_character_pairs("1!2@3#4$5%6^7&8*9(0)")
    print(r0)
    r1 = KeyRow.from_characters("qwertyuiop")
    r2 = KeyRow.from_characters("asdfghjkl")
    r2.append(Key(";", ":"))
    r3 = KeyRow.from_characters("zxcvbnm")
    r3.append(Key(",", "<"))
    r3.append(Key(".", ">"))
    r3.append(Key("/", "?"))
    keyboard = Keyboard()
    for row, offset in zip((r0, r1, r2, r3), offsets):
        keyboard.add_row(row, offset)
    return keyboard


def test_Keyboard_add_row():
    offsets: tuple[float, float, float, float] = (0, 0, 1, 1.5)
    keyboard = get_test_keyboard(offsets)
    assert keyboard.num_rows == 4
    assert keyboard.num_keys == sum(len(row) for row in keyboard.rows)
    # check keymap
    assert keyboard["q"] == keyboard.rows[1][0]
    assert keyboard["Q"] == keyboard.rows[1][0]
    assert keyboard[";"] == keyboard.rows[2][-1]
    assert keyboard["/"] == keyboard.rows[-1][-1]
    # check rows and positions
    for i, row_offset in enumerate(zip(keyboard.rows, offsets)):
        row, offset = row_offset
        for j, key in enumerate(row):
            assert key.position.x == j + offset
            assert key.position.y == -i


def test_Keyboard_add_rows():
    r0 = KeyRow.from_characters("1234567890")
    r1 = KeyRow.from_characters("qwertyuiop")
    rows = [r0, r1]
    keyboard = Keyboard()
    keyboard.add_rows(rows)
    assert keyboard.rows[0][0].value == "1"
    assert keyboard.rows[1][-1].value == "p"
    keyboard = Keyboard()
    with pytest.raises(ValueError):
        keyboard.add_rows(rows, [0])
    with pytest.raises(ValueError):
        keyboard.add_rows(rows, [0] * (len(rows) + 1))
    keyboard.add_rows(rows, [1] * len(rows))
    assert keyboard["1"].position == Point(1, 0)
    assert keyboard["p"].position == Point(len(r1), -1)


def test_Keyboard_add_row_from_characters():
    keyboard = Keyboard()
    keyboard.add_row_from_characters("asdf", 3)
    assert keyboard["a"].value == "a"
    assert keyboard.rows[0][0].shift_value == "A"
    assert keyboard["a"].position.x == 3


def test_Keyboard_add_rows_from_characterss():
    keyboard = Keyboard()
    keyboard.add_rows_from_character_sets(["asdf", "zxcv"])
    assert keyboard.rows[0][0].value == "a"
    assert keyboard.rows[1][-1].value == "v"


def test_Keyboard_str():
    keyboard = Keyboard()
    keyboard.add_rows_from_character_sets(["asdf", "zxcv"])
    assert str(keyboard) == "aA sS dD fF\nzZ xX cC vV"


def test_Keyboard_get_key():
    keyboard = get_test_keyboard()
    assert keyboard.get_key("q") == keyboard.rows[1][0]
    assert keyboard.get_key(Point(0, 0)) == keyboard.rows[0][0]


def test_Keyboard_get_position():
    keyboard = get_test_keyboard()
    assert keyboard.get_position("1") == Point(0, 0)
    assert keyboard.get_position("/") == Point(
        len(keyboard.rows[-1]) - 1, -1 * (keyboard.num_rows - 1)
    )


def test_Keyboard_get_distance():
    keyboard = get_test_keyboard()
    # 3-4-5 triangle
    assert keyboard.get_distance("1", "b") == 5


def test_Keyboard_get_vector():
    keyboard = get_test_keyboard()
    # 3-4-5 triangle
    assert keyboard.get_vector("1", "b") == Point(4, -3)


def test_Keyboard_keys():
    keyboard = get_test_keyboard()
    assert keyboard.num_keys == len(keyboard.keys)


def test_Keyboard_get_bounds():
    keyboard = get_test_keyboard()
    bounds = keyboard.get_bounds()
    assert keyboard.get_position("1") == bounds.top_left
    assert keyboard.get_position("/") == bounds.bottom_right
    assert keyboard.get_position("0") == bounds.top_right
    assert keyboard.get_position("z") == bounds.bottom_left


def test_Keyboard_get_key_bounds():
    keyboard = get_test_keyboard()
    # These are the corner characters, so should be the same as the keyboard bounds
    bounds = keyboard.get_key_bounds("1/0z")
    assert bounds == keyboard.get_bounds()


def test_Keyboard_get_path_bounds():
    keyboard = get_test_keyboard()
    # goes from start to end of top row
    # then down one and then to the start of that row.
    # Should produce bounds with `right` equal to distance from '1' to '0'
    # `left` equal to distance from 'p' to 'q'
    # `top` equal to 0 (no upward traversal)
    # `bottom` equal to -1
    bounds = keyboard.get_path_bounds("10pq")
    assert bounds.right == keyboard.get_distance("1", "0")
    # -1 b/c distance has no direction component
    assert bounds.left == -1 * keyboard.get_distance("p", "q")
    assert bounds.top == 0
    assert bounds.bottom == -1


def test_Keyboard_get_path():
    sequence = "asdf"
    keyboard = get_test_keyboard()
    path = keyboard.get_path(sequence)
    for vector in path:
        assert vector == Point(1, 0)
    sequence = "vdw1"
    path = keyboard.get_path(sequence)
    for vector in path:
        assert vector == Point(-1, 1)


def test_Keyboard_contains():
    keyboard = get_test_keyboard()
    assert "a" in keyboard
    assert "-" not in keyboard
    assert Point(0, 0) in keyboard
    assert Point(-100, -100) not in keyboard


def test_Keyboard_characters():
    keyboard = Keyboard()
    keyboard.add_row_from_characters("asdf")
    characters = keyboard.characters
    # Each of the added keys should also have an upper case character
    assert len(characters) == 8
    assert all(ch in characters for ch in "asdfASDF")


def test_Keyboard_get_key_relative_to_character():
    keyboard = get_test_keyboard()
    assert keyboard.get_key_relative_to_character("a", 0, 1) == keyboard["q"]
    assert keyboard.get_key_relative_to_character("A", 0, 1) == keyboard["q"]
    assert keyboard.get_key_relative_to_character("a", 1, 1) == keyboard["w"]
    assert keyboard.get_key_relative_to_character("a", 1, 0) == keyboard["s"]
    assert keyboard.get_key_relative_to_character("a", 1, -1) == keyboard["x"]
    assert keyboard.get_key_relative_to_character("a", 0, -1) == keyboard["z"]
    assert keyboard.get_key_relative_to_character("a", -1, -1) is None
    assert keyboard.get_key_relative_to_character("a", -1000, 1000) is None
    assert keyboard.get_key_relative_to_character("a", 3, 2) == keyboard["4"]


def test_Keyboard_index():
    keyboard = get_test_keyboard()
    assert keyboard.index("1") == Point(0, 0)
    assert keyboard.index("!") == Point(0, 0)
    assert keyboard.index("2") == Point(1, 0)
    assert keyboard.index("w") == Point(1, 1)


def test_Keyboard_get_keys_within_bounds_of_character():
    keyboard = get_test_keyboard()
    bounds = Bounds(-1, 1, 1, -1)
    center_char = "s"
    expected_chars = "qweadzxc"
    keys = keyboard.get_keys_within_bounds_of_character(center_char, bounds)
    assert len(keys) == len(expected_chars)
    for key in keys:
        assert key.value != center_char
        assert key.value in expected_chars


def test_Keyboard_get_keys_within_bounds_of_character_at_edge():
    keyboard = get_test_keyboard()
    bounds = Bounds(-1, 1, 1, -1)
    center_char = "q"
    expected_chars = "12wsa"
    keys = keyboard.get_keys_within_bounds_of_character(center_char, bounds)
    assert len(keys) == len(expected_chars)
    for key in keys:
        assert key.value != center_char
        assert key.value in expected_chars


def test_Keyboard_get_keys_within_bounds_of_character_non_unit():
    keyboard = get_test_keyboard()
    bounds = Bounds(0, 0, 3, -2)
    center_char = "q"
    expected_chars = "werasdfzxcv"
    keys = keyboard.get_keys_within_bounds_of_character(center_char, bounds)
    assert len(keys) == len(expected_chars)
    for key in keys:
        assert key.value != center_char
        assert key.value in expected_chars


# =================================== KeyPlotter ===================================


def run_plot_test(func: Callable[..., Figure], keyboard: Keyboard, **kwargs: Any):
    fig = func(keyboard, **kwargs)
    fig.show()
    response = Confirm.ask("Does this look correct?")
    fig.clear()
    if not response:
        raise Exception(f"`{func.__qualname__}()` did not show expected appearance.")


@pytest.mark.plot
def test_KeyPlotter_plot_keyboard():
    keyboard = get_test_keyboard()
    run_plot_test(KeyPlotter.plot_keyboard, keyboard)
    run_plot_test(KeyPlotter.plot_keyboard, keyboard, key_style=KeyStyle.VALUE_ONLY)
    run_plot_test(
        KeyPlotter.plot_keyboard, keyboard, key_style=KeyStyle.SHIFT_VALUE_ONLY
    )


@pytest.mark.plot
def test_KeyPlotter_plot_entry():
    keyboard = get_test_keyboard()
    entry = "aJu30v"
    run_plot_test(KeyPlotter.plot_entry, keyboard, entry=entry)
    run_plot_test(
        KeyPlotter.plot_entry, keyboard, entry=entry, key_style=KeyStyle.VALUE_ONLY
    )
    run_plot_test(
        KeyPlotter.plot_entry,
        keyboard,
        entry=entry,
        key_style=KeyStyle.SHIFT_VALUE_ONLY,
    )
