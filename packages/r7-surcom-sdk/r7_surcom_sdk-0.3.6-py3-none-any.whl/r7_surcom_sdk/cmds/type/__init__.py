
from r7_surcom_sdk.cmds.type.generate import GenerateCommand
from r7_surcom_sdk.cmds.type.install import InstallCommand
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKMainCommand


class TypesCmd(SurcomSDKMainCommand):

    """
    [help]
    Manage {PRODUCT_NAME} Types
    ---

    [description]
    These commands allow you to develop and manage Types for the {PLATFORM_NAME}.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} generate
    ---
    """
    def __init__(self, parent_parser):

        cmd_docstr = self.__doc__.format(
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=constants.CMD_TYPES
        )

        super().__init__(
            parent=parent_parser,
            cmd_name=constants.CMD_TYPES,
            cmd_docstr=cmd_docstr
        )

        # Add sub commands
        self.cmd_generate = GenerateCommand(self.cmd_parser)
        self.cmd_install = InstallCommand(self.cmd_parser)

    def run(self, args):

        if args.type == constants.CMD_GENERATE:
            self.cmd_generate.run(args)

        elif args.type == constants.CMD_INSTALL:
            self.cmd_install.run(args)

        else:
            self.main_parser.print_help()
