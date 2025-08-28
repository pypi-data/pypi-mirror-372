
from typing import Callable

from r7_surcom_sdk.lib import SurcomSDKException, constants


class Validation(object):
    """
    Represents a validation that can be run against a Legacy or a Surcom Connector
    """

    def __init__(
        self,
        title: str,
        fn: Callable,
        solution: str = None,
        level: str = constants.ISSUE_LEVEL_CRITICAL,
        skip: bool = False,
        ci_only: bool = False,
        fail_fast: bool = False
    ):
        """
        Initialize a Validation object

        :param title: The title of the validation
        :type title: str
        :param fn: The function to run for the validation
        :type fn: Callable
        :param solution: The solution to apply if the validation fails, defaults to None
        :type solution: str, optional
        :param level: The level of the validation, defaults to constants.ISSUE_LEVEL_CRITICAL
        :type level: str, optional
        :param skip: Whether to skip the validation, defaults to False
        :type skip: bool, optional
        :param ci_only: Whether the validation is only for CI, defaults to False
        :type ci_only: bool, optional
        :param fail_fast: Whether to fail fast on the validation, defaults to False
        :type fail_fast: bool, optional
        :raises SurcomSDKException: If the level is not valid
        """
        self.title = title
        self.fn = fn
        self.solution = solution
        self.skip = skip
        self.ci_only = ci_only
        self.fail_fast = fail_fast

        if level not in constants.VALID_LEVELS:
            raise SurcomSDKException(f"'{level}' is not a valid level. Valid levels are {constants.VALID_LEVELS}")

        self.level = level
