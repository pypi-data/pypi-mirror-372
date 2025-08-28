import random
import string

import pytest

from shouldersurfscore.classes import password_rules
from shouldersurfscore.classes.keyboard import Keyboard
from shouldersurfscore.classes.password_validator import PasswordValidator


def test_password_rule():
    class LengthRule(password_rules.PasswordRule):
        def __init__(self, min_length: int, max_length: int):
            self.min_length = min_length
            self.max_length = max_length

        def is_valid(self, password: str) -> bool:
            return self.min_length <= len(password) <= self.max_length

    rule = LengthRule(5, 10)
    assert not rule.is_valid("1" * 3)
    assert rule.is_valid("1" * 5)
    assert rule.is_valid("1" * 8)
    assert rule.is_valid("1" * 10)
    assert not rule.is_valid("1" * 20)


def test_variable_length_rule_setters():
    with pytest.raises(ValueError):
        password_rules.VariableLengthPasswordRule(10, 1)
    with pytest.raises(ValueError):
        password_rules.VariableLengthPasswordRule(-100)
    rule = password_rules.VariableLengthPasswordRule(5)
    with pytest.raises(ValueError):
        rule.max_length = 0
    with pytest.raises(ValueError):
        rule.min_length = 0
    rule.max_length = 10
    with pytest.raises(ValueError):
        rule.min_length = 11


def test_variable_length_rule_validity():
    rule = password_rules.VariableLengthPasswordRule(5)
    assert not rule.is_valid("1" * 3)
    assert not rule.is_valid("")
    assert rule.is_valid("1" * 5)
    assert rule.is_valid("1" * 8)
    assert rule.is_valid("1" * 800)
    rule.max_length = 10
    assert rule.is_valid("1" * 10)
    assert not rule.is_valid("1" * 100)
    rule.min_length = rule.max_length
    assert rule.is_valid("1" * rule.min_length)
    assert not rule.is_valid("1" * (rule.min_length + 1))


def test_prohibited_rule_validity():
    passwords = ["admin", "password", "AdMiN", "passwoRD"]
    # case-insensitive
    rule = password_rules.ProhibitedPasswordRule(passwords)
    assert rule.is_valid("asdf")
    assert not rule.is_valid("admin")
    assert not rule.is_valid("ADMIN")
    # case-sensitive
    rule = password_rules.ProhibitedPasswordRule(passwords, True)
    assert rule.is_valid("asdf")
    assert not rule.is_valid("admin")
    assert rule.is_valid("ADMIN")
    assert not rule.is_valid("AdMiN")
    # check for partial matching
    assert not rule.is_valid("passwordpasswordadmin")
    # no partial matching
    rule = password_rules.ProhibitedPasswordRule(passwords, partial_matching=False)
    assert rule.is_valid("passwordpasswordadmin")


def test_fixed_length_rule_validity():
    lengths: list[int] = []
    with pytest.raises(ValueError):
        password_rules.FixedLengthPasswordRule(lengths)
    lengths = [4, 6]
    rule = password_rules.FixedLengthPasswordRule(lengths)
    assert rule.is_valid("1" * lengths[0])
    assert rule.is_valid("1" * lengths[1])
    assert not rule.is_valid("1" * 100)


def test_no_sequential_rule_validity():
    keyboard = Keyboard()
    keyboard.add_rows_from_character_sets(["qwert", "asdfg", "zxcvb"])
    rule = password_rules.NoSequentialKeysPasswordRule(keyboard.keys)
    assert not rule.is_valid("qwer")
    assert not rule.is_valid("wer")
    assert not rule.is_valid("qwert")
    assert not rule.is_valid("qwertt")
    assert not rule.is_valid("QWERT")
    assert not rule.is_valid("qWeRtT")
    assert not rule.is_valid("qwerTta")
    assert not rule.is_valid("rEwq")
    assert rule.is_valid("qwerts")
    assert rule.is_valid("qwERts")
    assert rule.is_valid("qweraS")
    assert rule.is_valid("dsre")


def test_no_mono_character_rule_validity():
    rule = password_rules.NoMonoCharacterPasswordRule()
    # This is valid because it isn't repeating
    # and this rule doesn't enforce a minimum length
    assert rule.is_valid("a")
    assert not rule.is_valid("aaa")
    assert not rule.is_valid("aAa")
    assert rule.is_valid("aba")


def test_typeable_characters_rule_validity():
    characters = "asdfzxcv><?"
    rule = password_rules.ValidCharactersPasswordRule(characters)
    assert rule.is_valid("a??ds")
    assert not rule.is_valid("as32df")
    assert rule.is_valid("")
    assert not rule.is_valid(" ")

    rule = password_rules.ValidCharactersPasswordRule("")
    assert rule.is_valid("")
    assert not rule.is_valid("asdf")


# ======================== Validator ============================
def test_empty_validator():
    # Any password should pass
    validator = PasswordValidator([])
    assert validator.is_valid("")
    characters = string.ascii_letters + string.digits + string.punctuation
    for i in range(10):
        password = "".join(random.sample(characters, i))
        assert validator.is_valid(password)


def test_validator():
    validator = PasswordValidator(
        [
            password_rules.VariableLengthPasswordRule(5, 10),
            password_rules.NoMonoCharacterPasswordRule(),
        ]
    )
    # Should satisfy both rules
    assert validator.is_valid("abcde")
    # Should only satisfy length rule
    assert validator.is_invalid("a" * 8)
    # Should only satisfy no mono rule
    assert validator.is_invalid("abc")
