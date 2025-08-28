
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKMainCommand
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.cmds.config.init import InitCommand
from r7_surcom_sdk.cmds.config.list_connections import ListConnectionsCommand
from r7_surcom_sdk.cmds.config.add_connection import AddConnectionCommand
from r7_surcom_sdk.cmds.config.delete_connection import DeleteConnectionCommand
from r7_surcom_sdk.cmds.config.test_connection import TestConnectionCommand
from r7_surcom_sdk.cmds.config.set_default import SetDefaultConnectionCommand
from r7_surcom_sdk.cmds.config.enable_tab_completion import EnableTabCompletionCommand


class ConfigCmd(SurcomSDKMainCommand):

    """
    [help]
    Configure the {FULL_PROGRAM_NAME}
    ---

    [description]
The {FULL_PROGRAM_NAME} uses a configuration file that is located at `{PATH_SURCOM_CONFIG_FILE}`. It
is an INI formatted file.

The {FULL_PROGRAM_NAME} supports multiple connections to different {PRODUCT_NAME} instances. You
can use these commands to manage your connections.

Any option in the {CONFIG_FILE_NAME} file can also be a 1Password Secret Reference. See our
documentation for more information on how to use 1Password with the {FULL_PROGRAM_NAME}.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} init
    ---
    """
    def __init__(self, parent_parser):

        cmd_docstr = self.__doc__.format(
            DISPLAY_NAME=constants.DISPLAY_NAME,
            FULL_PROGRAM_NAME=constants.FULL_PROGRAM_NAME,
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            PATH_SURCOM_CONFIG_FILE=constants.PATH_SURCOM_CONFIG_FILE,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
            COMMAND=constants.CMD_CONFIG
        )

        super().__init__(
            parent=parent_parser,
            cmd_name=constants.CMD_CONFIG,
            cmd_docstr=cmd_docstr
        )

        # Add sub commands
        self.cmd_init = InitCommand(self.cmd_parser)
        self.cmd_add_connection = AddConnectionCommand(self.cmd_parser)
        self.cmd_test_connection = TestConnectionCommand(self.cmd_parser)
        self.cmd_delete_connection = DeleteConnectionCommand(self.cmd_parser)
        self.cmd_list_connections = ListConnectionsCommand(self.cmd_parser)
        self.cmd_set_active = SetDefaultConnectionCommand(self.cmd_parser)
        self.cmd_enable_tabs = EnableTabCompletionCommand(self.cmd_parser)

    def run(self, args):

        if args.config == constants.CMD_INIT:
            self.cmd_init.run(args)

        elif args.config == constants.CMD_LIST_CONNECTIONS:
            self.cmd_list_connections.run(args)

        elif args.config == constants.CMD_ADD_CONNECTION:
            self.cmd_add_connection.run(args)

        elif args.config == constants.CMD_TEST_CONNECTION:
            self.cmd_test_connection.run(args)

        elif args.config == constants.CMD_DELETE_CONNECTION:
            self.cmd_delete_connection.run(args)

        elif args.config == constants.CMD_SET_ACTIVE:
            self.cmd_set_active.run(args)

        elif args.config == constants.CMD_ENABLE_TABS:
            self.cmd_enable_tabs.run(args)

        else:
            self.main_parser.print_help()
