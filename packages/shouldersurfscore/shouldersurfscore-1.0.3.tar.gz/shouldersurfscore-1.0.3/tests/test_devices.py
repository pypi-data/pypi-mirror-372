import datetime

import pytest

from shouldersurfscore.classes.device import InvalidPasswordError
from shouldersurfscore.equipment.devices import Devices


def test_iphone():
    # Timeout numbers from here:
    #  - https://www.simplymac.com/ios/what-is-the-maximum-lockout-time-on-iphone
    device = Devices.get_iphone()
    assert device.gatekeeper.max_attempts == 10
    device.unlock(None)
    # check pin lengths (4 and 6) and allowed characters (numeric only)
    with pytest.raises(InvalidPasswordError):
        device.set_password("12")
    with pytest.raises(InvalidPasswordError):
        device.set_password("12345")
    with pytest.raises(InvalidPasswordError):
        device.set_password("abcd")
    device.lock()
    for _ in range(device.gatekeeper.max_attempts):
        device.unlock("wrong")
    assert device.gatekeeper.elapsed_time == datetime.timedelta(
        minutes=1
    ) + datetime.timedelta(minutes=5) + datetime.timedelta(
        minutes=15
    ) + datetime.timedelta(
        minutes=60
    )
