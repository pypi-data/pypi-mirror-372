import logging

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, formats

LOG = logging.getLogger(constants.LOGGER_NAME)


class EnableTabCompletionCommand(SurcomSDKSubCommand):
    """
    [help]
    Enable Tab Completion for the {FULL_PROGRAM_NAME}
    ---

    [description]
    With this {FULL_PROGRAM_NAME} command, we active argcomplete by running
the `activate-global-python-argcomplete` command in a sub process

See more at: https://pypi.org/project/argcomplete/
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_ENABLE_TABS

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            FULL_PROGRAM_NAME=constants.FULL_PROGRAM_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Enabling Tab Completion in you shell for the "
                                  f"{constants.FULL_PROGRAM_NAME}", divider=True)

        p = sdk_helpers.run_subprocess(["activate-global-python-argcomplete", "--yes"])

        stderr = getattr(p, "stderr", None)

        if stderr:
            msg = stderr.decode("utf-8").strip()
            sdk_helpers.print_log_msg(f"{msg}", log_level=logging.WARNING)

            if "restart your shell" not in msg:
                raise SurcomSDKException(
                    "Failed to enable tab completion",
                    solution="Make sure you have 'argcomplete' installed and try again"
                )

            sdk_helpers.print_log_msg(
                "Tab completion now enabled. Just restart your shell!",
                log_color=colors.OKGREEN,
                log_format=formats.BOLD
            )

        else:
            raise SurcomSDKException(
                "Failed to enable tab completion",
                solution="Make sure you have 'argcomplete' installed and try again"
            )

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
