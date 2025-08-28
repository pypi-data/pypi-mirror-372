import logging

from r7_surcom_sdk.lib import (SurcomAPI, SurcomSDKException, constants,
                               sdk_config, sdk_helpers)
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, formats

LOG = logging.getLogger(constants.LOGGER_NAME)


class TestConnectionCommand(SurcomSDKSubCommand):
    """
    [help]
    Test the {FULL_PROGRAM_NAME} is configured correctly with {PRODUCT_NAME}
    ---

    [description]
    Read the current Active Connection from the config file and test it
by making a request to the {PRODUCT_NAME} API with the API Key
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_TEST_CONNECTION

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            FULL_PROGRAM_NAME=constants.FULL_PROGRAM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Test the Active Connection", divider=True)

        conn = sdk_config.get_default_connection()

        surcom_client = SurcomAPI(
            base_url=conn.url,
            api_key=conn.api_key,
            user_agent_str=f"{self.cmd_name} {self.sub_cmd_name}"
        )

        sdk_helpers.print_log_msg(
            f"Testing we can reach the {constants.PRODUCT_NAME} API with '{conn.name}'...",
            log_level=logging.WARNING
        )

        status = surcom_client.app_status(constants.NOETIC_BUILTINS_ID)

        if status.lower() != constants.STATUS_OK:
            raise SurcomSDKException(
                f"Failed to connect to the {constants.PLATFORM_NAME} using the Active Connection",
                solution=f"Check your API Key and URL in the config file at '{constants.PATH_SURCOM_CONFIG_FILE}'",
            )

        sdk_helpers.print_log_msg(
            f"Successfully connected to the {constants.PRODUCT_NAME} using '{conn.name}'",
            log_color=colors.OKGREEN,
            log_format=formats.BOLD
        )

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
