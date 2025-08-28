import pytest

from shouldersurfscore.classes import gatekeeper, timeouts


class GateChecker:
    def __init__(
        self,
        gk: gatekeeper.GateKeeper,
        expected_attempts_made: int,
        expected_elapsed_time: float,
    ):
        self.gk = gk
        self.expected_attempts_made = expected_attempts_made
        self.expected_elapsed_time = expected_elapsed_time

    def assert_attributes(self):
        assert self.gk.attempts_made == self.expected_attempts_made
        if self.gk.max_attempts:
            assert self.gk.attempts_remaining == (
                self.gk.max_attempts - self.gk.attempts_made
            )
        else:
            assert self.gk.attempts_remaining == None
        assert self.gk.elapsed_time.total_seconds() == self.expected_elapsed_time

    def assert_gatestate(self) -> None:
        raise NotImplementedError()

    def assert_exceptions(self):
        pass

    @classmethod
    def check(
        cls,
        gk: gatekeeper.GateKeeper,
        expected_attempts_made: int,
        expected_elapsed_time: float,
    ):
        checker = cls(gk, expected_attempts_made, expected_elapsed_time)
        checker.assert_attributes()
        checker.assert_gatestate()
        checker.assert_exceptions()


class UnlockedGateChecker(GateChecker):
    def assert_gatestate(self):
        assert self.gk.status == gatekeeper.Gate.UNLOCKED
        assert self.gk.is_unlocked
        assert not self.gk.is_locked
        assert not self.gk.is_locked_out

    def assert_exceptions(self):
        with pytest.raises(gatekeeper.UnlockedError):
            self.gk.unlock(self.gk._password)  # type:ignore


class LockedGateChecker(GateChecker):
    def assert_exceptions(self):
        # Can't change password when locked/locked out
        with pytest.raises(gatekeeper.LockedError):
            self.gk.set_password(None)
        # Can't change timeout when locked/locked out
        with pytest.raises(gatekeeper.LockedError):
            self.gk.set_timeout(timeouts.ConstantTimeout())
        # Can't change max_attempts:
        with pytest.raises(gatekeeper.LockedError):
            self.gk.max_attempts = 10
        # Can't lock when not unlocked
        with pytest.raises(gatekeeper.LockedError):
            self.gk.lock()

    def assert_gatestate(self):
        assert self.gk.status == gatekeeper.Gate.LOCKED
        assert self.gk.is_locked
        assert not self.gk.is_unlocked
        assert not self.gk.is_locked_out


class LockedOutGateChecker(LockedGateChecker):
    def assert_gatestate(self):
        assert self.gk.status == gatekeeper.Gate.LOCKED_OUT
        assert self.gk.is_locked_out
        assert not self.gk.is_unlocked
        assert not self.gk.is_locked

    def assert_exceptions(self):
        super().assert_exceptions()
        # Can't attempt unlock
        with pytest.raises(gatekeeper.LockedOutError):
            self.gk.unlock(None)


def test_gatekeeper_init():
    gk = gatekeeper.GateKeeper()
    LockedGateChecker.check(gk, 0, 0)
    assert gk.max_attempts == None
    with pytest.raises(ValueError):
        gatekeeper.GateKeeper(None, -1)


def test_default_gatekeeper():
    gk = gatekeeper.GateKeeper()
    # No password was set, so should unlock with `None`
    # but not with anything else
    assert not gk.unlock("somepass")
    LockedGateChecker.check(gk, 1, 0)

    assert gk.unlock(None)
    UnlockedGateChecker.check(gk, 2, 0)


def test_gatekeeper_password():
    password = "123"
    gk = gatekeeper.GateKeeper(password)
    LockedGateChecker.check(gk, 0, 0)
    # No max tries and no timeout
    i = 0
    for _ in range(1000):
        i += 1
        assert not gk.unlock("wrongpass")
    LockedGateChecker.check(gk, i, 0)
    assert gk.unlock(password)
    UnlockedGateChecker.check(gk, i + 1, 0)


def test_gatekeeper_lockout():
    max_attempts = 10
    gk = gatekeeper.GateKeeper(max_attempts=max_attempts)
    LockedGateChecker.check(gk, 0, 0)
    with pytest.raises(gatekeeper.LockedOutError):
        for i in range(max_attempts + 1):
            assert not gk.unlock("wrongpass")
            if (i + 1) < max_attempts:
                LockedGateChecker.check(gk, i + 1, 0)
            else:
                LockedOutGateChecker.check(gk, max_attempts, 0)
    # Extra check that you can't enter correct password
    with pytest.raises(gatekeeper.LockedOutError):
        gk.unlock(None)


def test_gatekeeper_timeout():
    max_attempts = 10
    increment = 1
    gk = gatekeeper.GateKeeper(
        None,
        max_attempts,
        timeouts.ConstantTimeout(timeouts.delta_from_seconds(increment)),
    )
    LockedGateChecker.check(gk, 0, 0)
    with pytest.raises(gatekeeper.LockedOutError):
        for i in range(max_attempts + 1):
            assert not gk.unlock("wrongpass")
            if (i + 1) < max_attempts:
                LockedGateChecker.check(gk, i + 1, (i + 1) * increment)
            else:
                LockedOutGateChecker.check(
                    gk, max_attempts, (max_attempts - 1) * increment
                )
    LockedOutGateChecker.check(gk, max_attempts, (max_attempts - 1) * increment)


def test_gatekeeper_reset():
    gk = gatekeeper.GateKeeper(
        None, 2, timeouts.ConstantTimeout(timeouts.delta_from_seconds(1))
    )
    LockedGateChecker.check(gk, 0, 0)
    gk.unlock("wrongpass")
    LockedGateChecker.check(gk, 1, 1)
    gk.reset()
    LockedGateChecker.check(gk, 0, 0)


def test_force_unlock():
    gk = gatekeeper.GateKeeper(
        timeout=timeouts.ConstantTimeout(timeouts.delta_from_seconds(1))
    )
    LockedGateChecker.check(gk, 0, 0)
    # for checking that nothing else gets reset
    gk.unlock("wrongpass")
    LockedGateChecker.check(gk, 1, 1)
    gk.force_unlock()
    UnlockedGateChecker.check(gk, 1, 1)
    # check that we can alter the password
    gk.set_password("pass")
    gk.lock()
    # should be reset after locking
    LockedGateChecker.check(gk, 0, 0)
