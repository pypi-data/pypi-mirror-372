import itertools

import pytest
from noiftimer import Timer
from typing_extensions import override

from shouldersurfscore.classes import guessing_strategies
from shouldersurfscore.equipment.components import Components


class GuessListStrategy(guessing_strategies.GuessingStrategy):
    def __init__(self, guesses: list[str]) -> None:
        self._guesses: list[str] = guesses

    @override
    def _get_guesses(self) -> list[str]:
        return self._guesses


def test_interface():
    guesses = ["abc", "123", "fdsa"]
    strategy = GuessListStrategy(guesses)
    for g1, g2 in zip(guesses, strategy):
        assert g1 == g2
    assert guesses[0] in strategy.guesses
    # check for caching
    strategy._guesses = ["aaa", "jjj", "lll"]  # type:ignore
    # Should still be the original guesses
    for original, subbed in zip(strategy, strategy._guesses):  # type: ignore
        assert original != subbed


def test_observed_guess_not_set():
    strategy = guessing_strategies.ObservedGuess()
    with pytest.raises(guessing_strategies.ObservedGuessNotSetError):
        strategy.observed_guess
    strategy.observed_guess = ""
    strategy.observed_guess


def test_observed_guess():
    strategy = guessing_strategies.ObservedGuess()
    strategy.observed_guess = "abc"
    assert len(strategy.guesses) == 1
    assert strategy.guesses[0] == "abc"


def test_swap_adjacent_characters():
    strategy = guessing_strategies.SwapAdjacentCharacters()
    strategy.observed_guess = "abcd"
    # Should produce "bacd", "acbd", and "abdc"
    expected = ["bacd", "acbd", "abdc"]
    assert len(strategy.guesses) == len(expected)
    for g1, g2 in zip(strategy, expected):
        assert g1 == g2


def test_sequential():
    strategy = guessing_strategies.BruteForceGuessing("1234", [2])
    expected = ["".join(guess) for guess in itertools.product("1234", repeat=2)]
    assert len(strategy.guesses) == len(expected)
    for g1, g2 in zip(strategy, expected):
        assert g1 == g2


def test_sequential_caching():
    timer = Timer().start()
    strategy = guessing_strategies.BruteForceGuessing("1234567890", [7])
    # trigger guess generation
    strategy.guesses
    timer.stop()
    print()
    print(timer.elapsed_str)
    assert timer.elapsed > 0
    # updating observed shouldn't recompute guesses for this one
    timer.start()
    strategy.observed_guess = ""
    strategy.guesses
    timer.stop()
    print(timer.elapsed_str)
    assert timer.elapsed == 0
    # just for coverage b/c techically the propery is overridden
    assert strategy.observed_guess == ""


def test_swap_adjacent_keys_no_shift():
    keyboard = Components.get_standard_keyboard()
    observed = "abc"
    expected = [
        "qbc",
        "wbc",
        "sbc",
        "xbc",
        "zbc",
        "avc",
        "afc",
        "agc",
        "ahc",
        "anc",
        "abx",
        "abs",
        "abd",
        "abf",
        "abv",
    ]
    strategy = guessing_strategies.SwapAdjacentKeys(keyboard, False)
    strategy.observed_guess = observed
    assert len(strategy.guesses) == len(expected)
    for guess in strategy.guesses:
        assert guess in expected


def test_swap_adjacent_keys_shift():
    keyboard = Components.get_standard_keyboard()
    observed = "abc"
    expected = [
        "qbc",
        "Qbc",
        "wbc",
        "Wbc",
        "sbc",
        "Sbc",
        "xbc",
        "Xbc",
        "zbc",
        "Zbc",
        "avc",
        "aVc",
        "afc",
        "aFc",
        "agc",
        "aGc",
        "ahc",
        "aHc",
        "anc",
        "aNc",
        "abx",
        "abX",
        "abs",
        "abS",
        "abd",
        "abD",
        "abf",
        "abF",
        "abv",
        "abV",
    ]
    strategy = guessing_strategies.SwapAdjacentKeys(keyboard, True)
    strategy.observed_guess = observed
    assert len(strategy.guesses) == len(expected)
    for guess in strategy.guesses:
        assert guess in expected


def test_swap_horizontally_adjacent_keys():
    keyboard = Components.get_standard_keyboard()
    observed = "abc"
    expected = [
        "sbc",
        "avc",
        "anc",
        "abx",
        "abv",
    ]
    strategy = guessing_strategies.SwapHorizontallyAdjacentKeys(keyboard, False)
    strategy.observed_guess = observed
    assert len(strategy.guesses) == len(expected)
    for guess in strategy.guesses:
        assert guess in expected


def test_swap_vertically_adjacent_keys():
    keyboard = Components.get_standard_keyboard()
    observed = "abc"
    expected = [
        "qbc",
        "zbc",
        "agc",
        "abd",
    ]
    strategy = guessing_strategies.SwapVerticallyAdjacentKeys(keyboard, False)
    strategy.observed_guess = observed
    assert len(strategy.guesses) == len(expected)
    for guess in strategy.guesses:
        assert guess in expected
