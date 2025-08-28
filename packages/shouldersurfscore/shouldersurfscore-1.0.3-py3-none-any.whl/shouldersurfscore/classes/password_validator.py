from collections.abc import Iterable

from shouldersurfscore.classes.password_rules import PasswordRule


class PasswordValidator:
    """
    Class for checking passwords against an arbitrary list of password rules.
    """

    def __init__(self, rules: Iterable[PasswordRule]) -> None:
        """
        Initialize the instance with a list of `PasswordRule` objects.

        Parameters
        ----------
        rules : Iterable[PasswordRule]
            The rules passwords should be checked against.
        """
        self._rules: Iterable[PasswordRule] = rules

    def is_valid(self, password: str) -> bool:
        """
        Whether the given password passes all rules.

        Parameters
        ----------
        password : str
            The password to validate.

        Returns
        -------
        bool
            Whether the password is valid according to the set of rules in this instance.
        """
        return all(rule.is_valid(password) for rule in self._rules)

    def is_invalid(self, password: str) -> bool:
        """
        Whether the given password fails any rules.

        Parameters
        ----------
        password : str
            The password to validate.

        Returns
        -------
        bool
            Whether the password is invalid according to the set of rules in this instance.
        """
        return not self.is_valid(password)
