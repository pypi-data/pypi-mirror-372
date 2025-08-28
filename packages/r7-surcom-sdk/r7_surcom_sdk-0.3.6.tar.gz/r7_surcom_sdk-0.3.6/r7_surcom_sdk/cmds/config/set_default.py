import logging

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class SetDefaultConnectionCommand(SurcomSDKSubCommand):
    """
    [help]
    Set the Active Connection
    ---

    [description]
    Set the Active Connection for the {PLATFORM_NAME}

Configure the {FULL_PROGRAM_NAME} to use a specific Connection Configuration
when connecting to {PRODUCT_NAME}

A 'Connection' is a section in the {CONFIG_FILE_NAME} file where its heading is prefixed
with 'connection.'
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} local
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} my-organization
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} example-customer
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_SET_ACTIVE

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
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

        sdk_helpers.print_log_msg("Set the Active Connection to use with the "
                                  f"{constants.DISPLAY_NAME}", divider=True)

        configs = sdk_config.get_configs(constants.PATH_SURCOM_CONFIG_FILE)

        if not configs:

            raise SurcomSDKException(
                "No configuration file found",
                solution="Run `surcom config init` to create one"
            )

        conn = sdk_config.get_connection_config(configs=configs, conn_name=args.name)

        sdk_config.update_defaults(configs=configs, new_default_conn=conn)

        sdk_config.write_config_file(config=configs)

        sdk_helpers.print_log_msg(f"The new active connection is: \n{conn}")

        sdk_helpers.print_log_msg(
            f"Finished running the '{self.sub_cmd_name}' command.\n\nTest the active connection with:\n"
            "> surcom config test",
            divider=True
        )
