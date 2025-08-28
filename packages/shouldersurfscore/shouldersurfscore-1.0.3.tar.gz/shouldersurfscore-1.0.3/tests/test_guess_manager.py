import itertools

import pytest
from test_guessing_strategies import GuessListStrategy

from shouldersurfscore.classes import password_rules
from shouldersurfscore.classes.guess_manager import GuessManager
from shouldersurfscore.classes.guessing_strategies import ObservedGuess
from shouldersurfscore.classes.password_validator import PasswordValidator


def test_observed():
    guesser = GuessManager("abc", [ObservedGuess()])
    assert len(guesser) == 1
    assert guesser.num_possible_guesses == 1
    assert guesser.num_guesses_made == 0
    assert guesser.history == []
    assert "abc" in guesser
    assert "123" not in guesser
    assert guesser.index("abc") == 0
    assert guesser.index("kisdlsfe") is None
    for guess in guesser:
        assert guess == "abc"
    assert guesser.history == ["abc"]
    assert guesser.num_guesses_made == 1


def test_multiple_strategies():
    observed = "pass"
    set1 = ["abc", "123", "pass"]
    set2 = ["444", "administrator", "123"]
    guesser = GuessManager(
        observed, [ObservedGuess(), GuessListStrategy(set1), GuessListStrategy(set2)]
    )

    expected: list[str] = []
    for guess in itertools.chain([observed], set1, set2):
        if guess not in expected:
            expected.append(guess)
    # Duplicates should be removed
    assert len(expected) == len((set([observed] + set1 + set2)))

    i = 0
    guessed: list[str] = []
    for g1, g2 in zip(guesser, expected):
        i += 1
        assert g1 == g2
        guessed.append(g1)
        assert guessed == guesser.history
        assert guesser.num_guesses_made == i
        assert guesser.index(g1) == i - 1


def test_with_validator():
    observed = "pass"
    set1 = ["abc", "123", "pass"]
    set2 = ["444", "administrator", "123"]
    validator = PasswordValidator([password_rules.NoMonoCharacterPasswordRule()])
    guesser = GuessManager(
        observed,
        [ObservedGuess(), GuessListStrategy(set1), GuessListStrategy(set2)],
        validator,
    )

    expected: list[str] = []
    for guess in itertools.chain([observed], set1, set2):
        if guess not in expected and validator.is_valid(guess):
            expected.append(guess)

    # "444" should have been removed
    assert "444" not in guesser
    assert len(expected) == (len((set([observed] + set1 + set2))) - 1)

    # Updating validator to `None` should not remove "444"
    guesser.set_password_validator(None)
    assert "444" in guesser
    # add one to left and substract one from right
    # to account for adding "444" back in
    assert len(expected) + 1 == (len((set([observed] + set1 + set2))))


def test_setting_observed():
    observed = "pass"
    guesser = GuessManager(observed, [ObservedGuess()])
    assert list(guesser) == ["pass"]
    guesser.set_observed_guess("word")
    assert list(guesser) == ["word"]
