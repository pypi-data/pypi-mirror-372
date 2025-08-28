import logging

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class AddConnectionCommand(SurcomSDKSubCommand):
    """
    [help]
    Add a Connection to the {CONFIG_FILE_NAME} file
    ---

    [description]
    Use this command to add a new Connection to the {FULL_PROGRAM_NAME} {CONFIG_FILE_NAME} file

This allows you to connect to multiple {PRODUCT_NAME} instances

The {FULL_PROGRAM_NAME} will prompt you for the details of the new Connection.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_ADD_CONNECTION

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            FULL_PROGRAM_NAME=constants.FULL_PROGRAM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Add a new Connection for {constants.DISPLAY_NAME}", divider=True)

        configs = sdk_config.get_configs(constants.PATH_SURCOM_CONFIG_FILE)

        if not configs:

            raise SurcomSDKException(
                "No configuration file found",
                solution="Run `surcom config init` to create one"
            )

        new_conn = sdk_config.prompt_for_new_connection()

        configs.add_section(new_conn.name)
        configs.set(new_conn.name, constants.CONFIG_NAME_URL, new_conn.original_url)
        configs.set(new_conn.name, constants.CONFIG_NAME_API_KEY, new_conn.api_key)
        configs.set(new_conn.name, constants.CONFIG_NAME_ACTIVE, str(new_conn.default))

        if new_conn.default:
            sdk_config.update_defaults(configs=configs, new_default_conn=new_conn)

        sdk_config.write_config_file(config=configs)

        sdk_helpers.print_log_msg(
            f"Finished running the '{self.sub_cmd_name}' command.\n\nTest the active connection with:\n"
            "> surcom config test",
            divider=True
        )
