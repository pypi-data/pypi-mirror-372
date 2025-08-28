

import os
import logging

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers, sdk_config
from r7_surcom_sdk.lib.surcom_api import SurcomAPI
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class InstallCommand(SurcomSDKSubCommand):
    """
    [help]
    Install a {PRODUCT_NAME} Type into the Platform
    ---

    [description]
    Use this command to install a type definition into {PRODUCT_NAME}.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} <path_to_type_definition.yaml>
    ---
    """
    def __init__(self, types_parser):

        self.cmd_name = constants.CMD_TYPES
        self.sub_cmd_name = constants.CMD_INSTALL

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=types_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr
        )

        self.cmd_parser.add_argument(Args.path_type.flag, **Args.path_type.kwargs)
        self.cmd_parser.add_argument(*Args.yes.flag, **Args.yes.kwargs)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(
            f"Starting the '{self.cmd_name} {self.sub_cmd_name}' command",
            divider=True
        )

        if not os.path.isfile(args.path_type) or not args.path_type.endswith('.yaml'):
            raise SurcomSDKException(
                f"Type schema file '{args.path_type}' does not exist or is not a valid YAML file",
                solution="Ensure you have provided a valid path to the type definition file"
            )

        connection = sdk_config.get_default_connection(prompt=True, default_to_yes=args.yes)

        surcom_client = SurcomAPI(
            base_url=connection.url,
            api_key=connection.api_key,
            user_agent_str=f"'{self.cmd_name} {self.sub_cmd_name}' command"
        )

        sdk_helpers.print_log_msg(
            f"Installing type from '{args.path_type}' into '{connection.name}'",
            divider=True
        )

        type_schema_content = sdk_helpers.read_file(path_to_file=args.path_type)

        surcom_client.types_create(content=type_schema_content)

        sdk_helpers.print_log_msg(f"Finished running the '{self.cmd_name} {self.sub_cmd_name}' command.", divider=True)
