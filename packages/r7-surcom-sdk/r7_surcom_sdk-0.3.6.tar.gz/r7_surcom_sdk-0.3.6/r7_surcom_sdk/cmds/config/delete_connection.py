import logging

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class DeleteConnectionCommand(SurcomSDKSubCommand):
    """
    [help]
    Delete a Connection from the {CONFIG_FILE_NAME} file
    ---

    [description]
    Use this command to delete a Connection from the {CONFIG_FILE_NAME} file

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_DELETE_CONNECTION

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            FULL_PROGRAM_NAME=constants.FULL_PROGRAM_NAME,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.cmd_parser.add_argument(Args.connection_name.flag, **Args.connection_name.kwargs)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Deleting a Connection", divider=True)

        configs = sdk_config.get_configs(constants.PATH_SURCOM_CONFIG_FILE)

        if not configs:

            raise SurcomSDKException(
                "No configuration file found",
                solution="Run `surcom config init` to create one"
            )

        connection_config = sdk_config.get_connection_config(
            configs=configs,
            conn_name=args.name
        )

        sdk_helpers.print_log_msg(
            f"Deleting '{connection_config.name}' from '{constants.PATH_SURCOM_CONFIG_FILE}'",
            log_level=logging.WARNING
        )

        sdk_config.delete_connection_config(
            configs=configs,
            conn_name=args.name
        )

        sdk_helpers.print_log_msg(f"Finished running the '{self.cmd_name} {self.sub_cmd_name}' command", divider=True)
