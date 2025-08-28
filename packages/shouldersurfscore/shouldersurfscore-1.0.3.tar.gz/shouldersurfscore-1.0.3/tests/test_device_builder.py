import pytest

from shouldersurfscore.classes.device import DeviceBuilder, InvalidPasswordError
from shouldersurfscore.classes.gatekeeper import Gate
from shouldersurfscore.classes.password_rules import (
    NoSequentialKeysPasswordRule,
    PasswordRule,
    VariableLengthPasswordRule,
)
from shouldersurfscore.classes.timeouts import ConstantTimeout, delta_from_seconds
from shouldersurfscore.equipment.components import Components


def test_default_builder():
    # no keyboard, no password, no timeouts, no max attempts
    device = DeviceBuilder.new().build()
    assert device.keyboard
    assert device.keyboard.characters == ""
    assert device.keyboard.keys == []
    assert device.is_locked
    assert not device.is_locked_out
    assert not device.is_unlocked
    assert device.gatekeeper.status == Gate.LOCKED
    assert device.gatekeeper.max_attempts is None
    assert device.gatekeeper.attempts_remaining is None
    # Should unlock with `None` password
    assert device.unlock(None)
    assert device.is_unlocked
    assert device.gatekeeper.attempts_made == 1
    device.lock()
    assert device.is_locked


def test_builder_with_keyboard():
    device = (
        DeviceBuilder.new()
        .set_keyboard(Components.get_standard_mobile_keyboard())
        .build()
    )
    assert device.keyboard
    # An automatic password rule should have been made
    # based on available keyboard characters
    # which in this case should only be alphabetic characters
    assert device.is_valid_password("slidksj")
    assert device.is_valid_password("sliKSsj")
    assert device.is_invalid_password("asldlk3782lcxv")
    # Check that the rule fires when setting password
    device.unlock(None)
    with pytest.raises(InvalidPasswordError):
        device.set_password("3332l39dk")
    device.set_password("yeehaw")
    device.lock()
    assert device.unlock("yeehaw")


def test_with_keyboard_and_password():
    # Numeric values can't be entered with this keyboard
    # so should raise error
    with pytest.raises(InvalidPasswordError):
        DeviceBuilder.new().set_keyboard(
            Components.get_standard_mobile_keyboard()
        ).set_password("387k3347").build()
    device = (
        DeviceBuilder.new()
        .set_keyboard(Components.get_standard_mobile_keyboard())
        .set_password("abc")
    ).build()
    device.unlock("abc")


def test_with_added_rules():
    keyboard = Components.get_standard_mobile_keyboard()
    with pytest.raises(InvalidPasswordError):
        DeviceBuilder.new().set_keyboard(keyboard).set_password(
            "asdf"
        ).add_password_rule(NoSequentialKeysPasswordRule(keyboard.keys)).build()
    password = "eiwls"
    device = (
        DeviceBuilder.new()
        .set_keyboard(keyboard)
        .set_password(password)
        .add_password_rule(NoSequentialKeysPasswordRule(keyboard.keys))
        .build()
    )
    assert device.unlock(password)
    with pytest.raises(InvalidPasswordError):
        device.set_password("lkjh")

    rules: list[PasswordRule] = [
        NoSequentialKeysPasswordRule(keyboard.keys),
        VariableLengthPasswordRule(5, 10),
    ]
    device = (
        DeviceBuilder.new()
        .set_keyboard(keyboard)
        .set_password("jeisldk")
        .set_password_rules(rules)
        .build()
    )
    assert device.unlock("jeisldk")
    with pytest.raises(InvalidPasswordError):
        device.set_password("lsi")
    with pytest.raises(InvalidPasswordError):
        device.set_password("asdfgh")


def test_with_max_unlock_attempts():
    device = (
        DeviceBuilder.new()
        .set_keyboard(Components.get_standard_mobile_keyboard())
        .set_password("yeehaw")
        .set_max_unlock_attempts(5)
        .build()
    )
    assert device.gatekeeper.max_attempts == 5
    assert device.gatekeeper.attempts_remaining == 5
    for _ in range(device.gatekeeper.max_attempts):
        assert not device.unlock("wrong")
    assert device.gatekeeper.attempts_remaining == 0
    assert device.is_locked_out


def test_with_timeout():
    device = (
        DeviceBuilder.new().set_timeout(ConstantTimeout(delta_from_seconds(1))).build()
    )
    assert device.gatekeeper.elapsed_time.total_seconds() == 0
    reps = 10
    for _ in range(reps):
        device.unlock("wrong")
    assert device.gatekeeper.elapsed_time.total_seconds() == reps
