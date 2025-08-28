
from r7_surcom_sdk.cmds.data.import_data import ImportCommand
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKMainCommand


class DataCmd(SurcomSDKMainCommand):

    """
    [help]
    Interact with {PRODUCT_NAME} Data
    ---

    [description]
    These commands allow you to work with data in the {PLATFORM_NAME}.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} import
    ---
    """
    def __init__(self, parent_parser):

        cmd_docstr = self.__doc__.format(
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=constants.CMD_DATA
        )

        super().__init__(
            parent=parent_parser,
            cmd_name=constants.CMD_DATA,
            cmd_docstr=cmd_docstr
        )

        # Add sub commands
        self.cmd_import = ImportCommand(self.cmd_parser)

    def run(self, args):

        if args.data == constants.CMD_IMPORT:
            self.cmd_import.run(args)

        else:
            self.main_parser.print_help()
