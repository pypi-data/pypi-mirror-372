"""
Module containing a custom exception for the r7_surcom_sdk
"""

import sys
import logging

from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, formats, fmt

LOG = logging.getLogger(constants.LOGGER_NAME)


class SurcomSDKException(Exception):

    # This should be set at the start of the run method for each command
    command_ran = None

    # This should be set to `True` if running in verbose mode
    debug_mode = False

    def __init__(
        self,
        message: str,
        print_stacktrace: bool = False,
        solution: str = None
    ):
        """
        Our main custom SDK exception

        By default we hide the stacktrace and only print the message
        that you pass in the error

        :param message: a short description of the error
        :type message: str
        :param print_stacktrace: if `True` print the exception traceback, else
            do not, defaults to `False`
        :type print_stacktrace: bool, optional
        :param solution: if provided, print the given solution at the end of the error
        :type solution: str, optional
        """

        if not print_stacktrace and not SurcomSDKException.debug_mode:

            # Override the default exception handler to
            # only print the error message and not the exception type
            def custom_except_hook(exctype, value, traceback):
                LOG.error(value)

            sys.excepthook = custom_except_hook

        if SurcomSDKException.command_ran:
            self.message = f"\n'{constants.PROGRAM_NAME} {SurcomSDKException.command_ran}' FAILED\n" \
                           f"{fmt('ERROR:', c=colors.FAIL, f=formats.BOLD)} {message}"

        else:
            self.message = f"\n'{constants.PROGRAM_NAME}' FAILED\n" \
                           f"{fmt('ERROR:', c=colors.FAIL, f=formats.BOLD)} {message}"

        if solution:
            self.message = f"{self.message}\n{fmt('Solution:', c=colors.WARNING, f=formats.BOLD)} {solution}"

        super(SurcomSDKException, self).__init__(message)

    def __str__(self):
        return self.message


class JSONRefResolveError(Exception):
    """
    Custom exception that is raised if we fail to resolve a reference
    """
    pass
