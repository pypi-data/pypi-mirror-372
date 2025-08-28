from typing import NamedTuple

import pytest

from shouldersurfscore.classes.device import Device, InvalidPasswordError
from shouldersurfscore.classes.gatekeeper import Gate, GateKeeper, LockedOutError
from shouldersurfscore.classes.password_rules import (
    NoSequentialKeysPasswordRule,
    ValidCharactersPasswordRule,
)
from shouldersurfscore.classes.password_validator import PasswordValidator
from shouldersurfscore.classes.timeouts import ConstantTimeout, delta_from_seconds
from shouldersurfscore.equipment.components import Components


class Defaults(NamedTuple):
    password: str = "abc"
    max_attempts: int = 10
    timeout_increment: int = 1


defaults = Defaults()


def get_test_device() -> Device:
    keyboard = Components.get_standard_mobile_keyboard()
    gatekeeper = GateKeeper(
        defaults.password,
        defaults.max_attempts,
        ConstantTimeout(delta_from_seconds(defaults.timeout_increment)),
    )
    password_validator = PasswordValidator(
        [
            ValidCharactersPasswordRule(keyboard.characters),
            NoSequentialKeysPasswordRule(keyboard.keys),
        ]
    )
    return Device(keyboard, gatekeeper, password_validator)


def test_initialization():
    device = get_test_device()
    assert device.is_locked
    assert not device.is_locked_out
    assert not device.is_unlocked
    gateinfo = device.gatekeeper
    assert gateinfo.status == Gate.LOCKED
    assert gateinfo.max_attempts == 10
    assert gateinfo.attempts_remaining == 10
    assert gateinfo.attempts_made == 0
    assert gateinfo.elapsed_time.total_seconds() == 0
    assert device.is_valid_password("slidksj")
    assert device.is_valid_password("sliKSsj")
    assert device.is_invalid_password("asldlk3782lcxv")


def test_unlock_lock():
    device = get_test_device()
    assert device.unlock(defaults.password)
    assert device.is_unlocked
    device.lock()
    assert device.is_locked


def test_set_new_password():
    device = get_test_device()
    device.unlock(defaults.password)
    # Only alphabetical characters should be allowed
    with pytest.raises(InvalidPasswordError):
        device.set_password("23l3k2")
    # No sequential keys either
    with pytest.raises(InvalidPasswordError):
        device.set_password("asdf")
    new_pass = "yeehaw"
    device.set_password(new_pass)
    device.lock()
    assert device.unlock(new_pass)
    # Set no password, should pass rules
    device.set_password(None)
    device.lock()
    assert device.unlock(None)


def test_lock_out():
    device = get_test_device()
    for _ in range(5):
        assert not device.unlock("wrong")
    gateinfo = device.gatekeeper
    assert gateinfo.attempts_made == 5
    assert gateinfo.attempts_remaining == 5
    assert (
        gateinfo.elapsed_time.total_seconds()
        == gateinfo.attempts_made * defaults.timeout_increment
    )
    for _ in range(5):
        assert not device.unlock("wrong")
    assert device.is_locked_out
    gateinfo = device.gatekeeper
    assert gateinfo.attempts_made == 10
    assert gateinfo.attempts_remaining == 0
    # substract 1 b/c final attempt doesn't accrue time
    # b/c transistion into lock out
    assert (
        gateinfo.elapsed_time.total_seconds()
        == (gateinfo.attempts_made - 1) * defaults.timeout_increment
    )


def test_reset():
    device = get_test_device()
    if device.gatekeeper.max_attempts is not None:
        for _ in range(device.gatekeeper.max_attempts * 100):
            try:
                device.unlock("wrong")
            except LockedOutError:
                device.reset()


def test_force_unlock():
    device = get_test_device()
    assert device.is_locked
    device.force_unlock()
    assert device.is_unlocked
