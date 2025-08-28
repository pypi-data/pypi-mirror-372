from shouldersurfscore.classes.keyboard import Keyboard
from shouldersurfscore.classes.keyrow import KeyRow


class Components:
    """
    Contains static methods for obtaining instances of pre-defined device components.
    """

    @staticmethod
    def get_standard_keyboard() -> Keyboard:
        """
        A standard U.S qwerty keyboard containing all character keys with their shift values included.<br>
        (No control keys like 'tab', 'enter', 'ctrl', etc.)

        The horizontal offsets for each row are as follows:<br>
        row 1 (starts with `): 0<br>
        row 2 (starts with q): 1.5<br>
        row 3 (starts with a): 2<br>
        row 4 (starts with z): 2.5

        Returns
        -------
        Keyboard
            A standard U.S. qwerty keyboard (character symbol keys only).
        """
        keyboard: Keyboard = Keyboard()
        keyboard.add_row(KeyRow.from_character_pairs("`~1!2@3#4$5%6^7&8*9(0)-_=+"))
        keyboard.add_row(
            KeyRow.from_characters("qwertyuiop")
            + KeyRow.from_character_pairs("[{]}\\|"),
            1.5,
        )
        keyboard.add_row(
            KeyRow.from_characters("asdfghjkl") + KeyRow.from_character_pairs(";:'\""),
            2,
        )
        keyboard.add_row(
            KeyRow.from_characters("zxcvbnm") + KeyRow.from_character_pairs(",<.>/?"),
            2.5,
        )
        return keyboard

    @staticmethod
    def get_standard_mobile_keyboard() -> Keyboard:
        """
        A standard U.S. qwerty mobile keyboard containing only alphabetic characters.

        The horizontal offsets for each row are as follows:<br>
        row 1 (starts with q): 0<br>
        row 2 (starts with a): 0.5<br>
        row 3 (starts with z): 1.5

        Returns
        -------
        Keyboard
            A standard U.S. qwerty mobile keyboard (alphabetic character keys only).
        """
        keyboard: Keyboard = Keyboard()
        keyboard.add_rows_from_character_sets(
            ["qwertyuiop", "asdfghjkl", "zxcvbnm"], [0, 0.5, 1.5]
        )
        return keyboard

    @staticmethod
    def get_standard_keypad() -> Keyboard:
        """
        A standard numeric keypad:
        >>> |   / * = |
        >>> | 7 8 9 - |
        >>> | 4 5 6 + |
        >>> | 1 2 3   |
        >>> | 0   .   |

        The horizontal offsets for each row are as follows:<br>
        row 1 (starts with /): 1<br>
        All other rows: 0

        Returns
        -------
        Keyboard
            A standard numeric keypad (character symbols only).
        """
        keypad: Keyboard = Keyboard()
        keypad.add_row(KeyRow.from_characters("/*="), 1)
        keypad.add_rows(
            [
                KeyRow.from_characters("789-"),
                KeyRow.from_characters("456+"),
                KeyRow.from_characters("123"),
                KeyRow.from_characters("0 ."),
            ],
        )
        return keypad

    @staticmethod
    def get_standard_mobile_keypad() -> Keyboard:
        """
        A standard mobile keypad:
        >>> | 1 2 3 |
        >>> | 4 5 6 |
        >>> | 7 8 9 |
        >>> | * 0 # |

        None of the rows have horizontal offsets.

        Returns
        -------
        Keyboard
            A standard mobile keypad.
        """
        keypad: Keyboard = Keyboard()
        keypad.add_rows(
            [
                KeyRow.from_characters("123"),
                KeyRow.from_characters("456"),
                KeyRow.from_characters("789"),
                KeyRow.from_characters("*0#"),
            ]
        )
        return keypad

    @staticmethod
    def get_standard_pin_keypad() -> Keyboard:
        """
        A standard pin keypad typically found on device lock screens:
        >>> | 1 2 3 |
        >>> | 4 5 6 |
        >>> | 7 8 9 |
        >>> |   0   |

        The last row ('0') has a horizontal offset of 1.

        Returns
        -------
        Keyboard
            A standard pin keypad.
        """
        keypad: Keyboard = Keyboard()
        keypad.add_rows(
            [
                KeyRow.from_characters("123"),
                KeyRow.from_characters("456"),
                KeyRow.from_characters("789"),
            ]
        )
        keypad.add_row_from_characters("0", 1)
        return keypad
