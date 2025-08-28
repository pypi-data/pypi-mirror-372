import configparser
import logging

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import fmt, formats

LOG = logging.getLogger(constants.LOGGER_NAME)


class InitCommand(SurcomSDKSubCommand):
    """
    [help]
    Create an initial {CONFIG_FILE_NAME} file if none exists
    ---

    [description]
    Create an initial config file and prompt for details of a new Connection

If its already configured just print the details of the current active Connection
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONFIG
        self.sub_cmd_name = constants.CMD_INIT

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
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

        sdk_helpers.print_log_msg(f"Initializing the {constants.FULL_PROGRAM_NAME}", divider=True)

        configs = sdk_config.get_configs(constants.PATH_SURCOM_CONFIG_FILE)

        if not configs:

            sdk_helpers.print_log_msg(
                "No configuration file found so we will create one!",
                log_level=logging.WARNING
            )

            path_connector_ws = sdk_helpers.get_cli_input(
                prompt=f"""{fmt(
                    '''Enter the path to your Connectors Workspace (normally the 'r7-surcom-connectors' repo)''',
                    f=formats.BOLD
                )}""",
                default=constants.CONFIG_DEFAULT_CONNECTOR_DEV
            )

            conn = sdk_config.prompt_for_new_connection(initial_prompt=True)

            config = configparser.ConfigParser()

            config.add_section(constants.CONFIG_SEC_MAIN)
            config.set(constants.CONFIG_SEC_MAIN, constants.CONFIG_NAME_PATH_CONNECTOR_WS, path_connector_ws)

            config.add_section(conn.name)
            config.set(conn.name, constants.CONFIG_NAME_URL, conn.original_url)
            config.set(conn.name, constants.CONFIG_NAME_API_KEY, conn.api_key)
            config.set(conn.name, constants.CONFIG_NAME_ACTIVE, str(conn.default))

            sdk_config.write_config_file(config=config)

        else:
            sdk_helpers.print_log_msg(f"The {constants.FULL_PROGRAM_NAME} is already configured",
                                      log_level=logging.WARNING)

            sdk_helpers.print_log_msg(f"Configuration file: '{constants.PATH_SURCOM_CONFIG_FILE}'")

            path_connector_ws = configs[constants.CONFIG_SEC_MAIN][constants.CONFIG_NAME_PATH_CONNECTOR_WS]
            sdk_helpers.print_log_msg(f"Connector workspace: '{path_connector_ws}'")

            default_connection = sdk_config.get_default_connection(constants.PATH_SURCOM_CONFIG_FILE)

            sdk_helpers.print_log_msg(f"Active connection:\n\n{default_connection}")

        sdk_helpers.print_log_msg(
            f"Finished running the '{self.sub_cmd_name}' command.\n\nTest the active connection with:\n"
            "> surcom config test",
            divider=True
        )
