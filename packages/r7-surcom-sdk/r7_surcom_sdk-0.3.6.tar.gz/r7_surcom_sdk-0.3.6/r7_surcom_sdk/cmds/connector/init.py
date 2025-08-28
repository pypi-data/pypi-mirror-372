import os

from r7_surcom_sdk.lib import (SurcomSDKException, constants, sdk_config,
                               sdk_helpers)
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import fmt, formats, colors


class InitCommand(SurcomSDKSubCommand):
    """
    [help]
    Initialize a New Connector
    ---

    [description]
    Prompt for some basic information, generate a {FILENAME} file and
write it to your Connector development workspace
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_INIT

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name,
            FILENAME=constants.CONN_SPEC_YAML
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Initializing a New Connector", divider=True)

        ws = sdk_config.get_path_connector_dev()

        dn_prompt = f"\n{fmt('Enter a Display Name', f=formats.BOLD)}\nValid characters 'a-z, A-Z, 0-9, (), SPACES'"
        c_display_name = sdk_helpers.get_cli_input(
            prompt=dn_prompt,
            valid_regex_str=r"^[a-z0-9A-Z\s()]+$"
        )

        # We try a derive an accurate default id based on the display name
        id_default = c_display_name.strip().lower()
        id_default = id_default.replace("(", "").replace(")", "")
        id_default = ''.join([c for c in id_default if not c.isdigit()])  # Remove numbers
        id_default = '.'.join(id_default.split())  # Replace any remaining whitespace with '.'

        id_prompt = f"\n{fmt('Enter an ID for the Connector', f=formats.BOLD)}\nValid characters 'a-z, .'"
        c_id = sdk_helpers.get_cli_input(
            prompt=id_prompt,
            valid_regex_str=r"^[a-z\.]+$",
            default=id_default
        )

        author_prompt = f"\n{fmt('Who is the Author?', f=formats.BOLD)}\nValid characters 'a-z, A-Z, 0-9, SPACES'"
        c_author = sdk_helpers.get_cli_input(
            prompt=author_prompt,
            valid_regex_str=r"^[a-zA-Z\s0-9]+$",
            default=sdk_helpers.get_user()  # Use the current computer user as default if found
        )

        template_data = {
            "connector_id": c_id,
            "display_name": c_display_name,
            "author": c_author,
            "type_prefix": sdk_helpers.get_prefix_from_id(c_id)
        }

        c_dirname = c_id.replace(".", "_")
        path_connector_dir = os.path.join(ws, c_dirname)

        if os.path.exists(path_connector_dir):
            raise SurcomSDKException(
                message=f"'{c_dirname}' already exists in your workspace at '{path_connector_dir}'",
                solution="Use a unique Connector ID, delete this directory or update your workspace path in "
                         "the config file"
            )

        conn_spec = sdk_helpers.render_jinja_template(
            template=constants.CONN_SPEC_YAML,
            templates_path=constants.TEMPLATE_PATH_CONNECTORS,
            data=template_data
        )

        sdk_helpers.write_file(
            path=os.path.join(path_connector_dir, constants.CONN_SPEC_YAML),
            contents=conn_spec.rendered_template
        )

        sdk_helpers.print_log_msg(f"Generated the '{constants.CONN_SPEC_YAML}' file with default settings for "
                                  f"the Connector '{c_id}' in '{path_connector_dir}'")

        sdk_helpers.print_log_msg(f"Now edit the '{constants.CONN_SPEC_YAML}' file, change into the "
                                  f"Connector directory and run the "
                                  "'surcom connector codegen' command to generate the boilerplate code",
                                  log_color=colors.BLUE, log_format=formats.BOLD)

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
