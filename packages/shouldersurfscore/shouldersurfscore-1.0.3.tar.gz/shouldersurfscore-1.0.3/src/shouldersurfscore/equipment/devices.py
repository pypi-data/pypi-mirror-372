import datetime

from shouldersurfscore.classes import device, password_rules, timeouts
from shouldersurfscore.equipment.components import Components


class Devices:
    @staticmethod
    def get_iphone() -> device.Device:
        keypad: device.Keyboard = Components.get_standard_pin_keypad()
        # Timeout numbers from here:
        #  - https://www.simplymac.com/ios/what-is-the-maximum-lockout-time-on-iphone
        timeout: timeouts.ArbitraryTimeout = timeouts.ArbitraryTimeout(
            ([datetime.timedelta()] * 5)
            + [
                datetime.timedelta(minutes=1),
                datetime.timedelta(minutes=5),
                datetime.timedelta(minutes=15),
                datetime.timedelta(minutes=60),
            ]
        )
        pin_lengths: password_rules.FixedLengthPasswordRule = (
            password_rules.FixedLengthPasswordRule([4, 6])
        )
        max_unlock_attempts = 10
        return (
            device.DeviceBuilder.new()
            .set_keyboard(keypad)
            .set_timeout(timeout)
            .add_password_rule(pin_lengths)
            .set_max_unlock_attempts(max_unlock_attempts)
            .build()
        )
