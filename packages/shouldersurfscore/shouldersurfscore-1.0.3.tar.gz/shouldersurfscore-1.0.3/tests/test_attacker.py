import pytest

from shouldersurfscore.classes.attacker import Attacker, BreakInNotAttemptedError
from shouldersurfscore.classes.device import Device
from shouldersurfscore.classes.guessing_strategies import (
    BruteForceGuessing,
    SwapAdjacentCharacters,
)
from shouldersurfscore.equipment.devices import Devices

test_password = "1234"
test_observed = "1324"


def get_locked_iphone() -> Device:
    device = Devices.get_iphone()
    device.unlock(None)
    device.set_password(test_password)
    device.lock()
    return device


def test_no_strategies():
    device = get_locked_iphone()
    attacker = Attacker([])
    with pytest.raises(BreakInNotAttemptedError):
        assert attacker.num_possible_guesses == 1
    assert attacker.attempts_made == 0
    assert not attacker.break_in(device, test_observed)
    assert attacker.num_possible_guesses == 1
    assert attacker.attempts_made == 1
    assert device.is_locked
    device.reset()
    assert attacker.break_in(device, test_password)
    assert device.is_unlocked
    # should be reset back to 0 when break_in called
    # so should still be 1 after
    assert attacker.attempts_made == 1


def test_strategies_success():
    device = get_locked_iphone()
    attacker = Attacker([SwapAdjacentCharacters()])
    assert attacker.break_in(device, test_observed)
    assert device.is_unlocked


def test_lockout():
    device = get_locked_iphone()
    device.unlock(test_password)
    # Should be the last produced by brute force strategy
    # and exceed max attempts to get to
    device.set_password("0000")
    device.lock()
    if not device.keyboard:
        raise ValueError("test device has no keyboard")
    attacker = Attacker([BruteForceGuessing(device.keyboard.characters, [4])])
    assert not attacker.break_in(device, test_observed)
    assert device.is_locked_out
    assert attacker.attempts_made == device.gatekeeper.max_attempts


def test_is_guess():
    attacker = Attacker([SwapAdjacentCharacters()])
    with pytest.raises(BreakInNotAttemptedError):
        attacker.is_guess(test_observed)
    attacker.break_in(get_locked_iphone(), test_observed)
    assert attacker.is_guess(test_password)
    assert attacker.is_guess(test_observed)
    assert not attacker.is_guess("asdf")


def test_index():
    attacker = Attacker([SwapAdjacentCharacters()])
    with pytest.raises(BreakInNotAttemptedError):
        attacker.index(test_observed)
    attacker.break_in(get_locked_iphone(), test_observed)
    # observed should be first
    assert attacker.index(test_observed) == 0
    # actual is "1234" and observed is "1324"
    # so with the second guess from the swap adjacent strategy
    # should be "1234", which would be the 3rd guess overall (index of 2)
    assert attacker.index(test_password) == 2
    assert attacker.index("asdf") is None
