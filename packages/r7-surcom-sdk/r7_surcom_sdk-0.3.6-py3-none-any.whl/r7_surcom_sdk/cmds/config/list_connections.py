import logging

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class ListConnectionsCommand(SurcomSDKSubCommand):
    """
    [help]
    List all the {PRODUCT_NAME} Connections that are configured
    ---

    [description]
    List all the {PRODUCT_NAME} Connections that are configured with the {FULL_PROGRAM_NAME}
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_LIST_CONNECTIONS

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

        sdk_helpers.print_log_msg(f"Listing the Connections for the {constants.FULL_PROGRAM_NAME}", divider=True)

        configs = sdk_config.get_configs(constants.PATH_SURCOM_CONFIG_FILE)

        if not configs:

            raise SurcomSDKException(
                "No configuration file found",
                solution="Run `surcom config init` to create one"
            )

        connections = sdk_config.get_all_connections(constants.PATH_SURCOM_CONFIG_FILE)

        if not connections:
            raise SurcomSDKException(
                "No connections are configured",
                solution="Run `surcom config add` to add one"
            )

        for conn in connections:
            if conn.default:
                sdk_helpers.print_log_msg(f"{conn}\n(active)")
            else:
                sdk_helpers.print_log_msg(conn)

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
