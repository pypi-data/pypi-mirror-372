"""
Module that handles argparse for the r7_surcom_sdk
"""
import os
from argparse import SUPPRESS, ArgumentParser, RawDescriptionHelpFormatter

from r7_surcom_sdk.lib import SurcomSDKException, constants


class Arg():
    def __init__(self, flag, **kwargs):
        self.flag = flag
        self.kwargs = kwargs


class Args():

    verbose = Arg(
        flag=("-v", "--verbose"),
        help="Set the log level to DEBUG",
        action="store_true"
    )

    version = Arg(
        flag="--version",
        help=f"Print the version of the {constants.PROGRAM_NAME} SDK and exit",
        action="store_true"
    )

    path_connector = Arg(
        flag=("-c", "--path-connector"),
        help="Path to the Connector (Default: Current Working Directory)",
        dest="path_connector",
        default=os.getcwd()
    )

    path_connector_zip = Arg(
        flag=("-z", "--zip"),
        help="Path to a Connector ZIP file",
        dest="path_connector_zip"
    )

    debug = Arg(
        flag=("-d", "--debug"),
        help="Enable debug mode for the Connector",
        dest="debug",
        action="store_true"
    )

    no_cache = Arg(
        flag="--no-cache",
        help="Force building a new Docker image",
        dest="no_cache",
        action="store_true"
    )

    import_data = Arg(
        flag="--import-data",
        help=f"Once the Function has ran, import the data into {constants.PRODUCT_NAME}",
        dest="import_data",
        action="store_true"
    )

    fn_name = Arg(
        flag=("-f", "--function-name"),
        help="Specify the name of the function to run",
        dest="fn_name",
    )

    settings = Arg(
        flag=("-s", "--settings"),
        help="Valid settings for the function in the format 'sname1=svalue1,sname2=svalue2'. "
             "Settings specified here will override the settings in the `surcom_config` file",
        dest="fn_settings",
    )

    dir_output = Arg(
        flag=("-o", "--output"),
        help="Path to the output directory (Default: Connector 'build' directory)",
        dest="dir_output",
    )

    dir_data = Arg(
        flag=("-d", "--path-data"),
        help="Path to the directory to use (Default: Connector 'build/output' directory)",
        dest="dir_data",
    )

    path_file = Arg(
        flag=("-f", "--path-file"),
        help="Path to a file to use",
        dest="path_file",
    )

    path_type = Arg(
        flag="path_type", help="Path to the Type definition file",
    )

    connection_name = Arg(
        flag="name",
        help="Name of the Connection"
    )

    keep_build_files = Arg(
        flag="--keep-build-files",
        help="If provided, we keep all the generated build files",
        action="store_true",
        dest="keep_build_files",
    )

    path_data_file = Arg(
        flag="path_data_file",
        help="Path to the data file to use",
    )

    max_items = Arg(
        flag="--max-items",
        help="Maximum number of items to process",
        dest="max_items",
    )

    multiple_connectors = Arg(
        flag="--multiple-connectors",
        help="Specify this to validate multiple connectors at once. If provided, we treat the "
             "value of `path_connector` as a directory containing multiple connectors",
        dest="multiple_connectors",
        action="store_true"
    )

    path_all_connectors_dir = Arg(
        flag="--all-connectors-dir",
        help="Path to all Connectors. Mainly used in CI (Default: Parent of the Current Working Directory)",
        dest="path_all_connectors_dir",
        default=os.path.dirname(os.getcwd())
    )

    skip_validations = Arg(
        flag="--skip-validations",
        help="Skip specific validations. You can provide multiple validation titles separated by spaces. "
             "Example: --skip-validations 'there is an icon' 'the documentation is valid'",
        nargs="*",
        default=[]
    )

    is_ci = Arg(
        flag="--is-ci",
        help="If provided, we treat this as a CI run",
        action="store_true"
    )

    yes = Arg(
        flag=("-y", "--yes"),
        help="If provided, reply 'yes' to all prompts",
        action="store_true",
    )


class SurcomSDKArgumentParser(ArgumentParser):

    def error(self, message):
        """
        We want to override the default error handling
        """
        raise SurcomSDKException(message)

    def format_help(self):
        """
        Overriding the default format_help method to show the description first,
        then the usage, and finally the rest of the help.
        """
        formatter = self._get_formatter()

        # Add description first
        if self.description:
            formatter.add_text(self.description)

        # Add usage after description
        formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)

        # Add the rest as normal
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        formatter.add_text(self.epilog)
        return formatter.format_help()


class SurcomSDKArgHelpFormatter(RawDescriptionHelpFormatter):
    """
    Use this class to override the default argparse formatter
    """

    def __init__(self, prog):
        super(SurcomSDKArgHelpFormatter, self).__init__(prog, max_help_position=60, width=110)

    def add_argument(self, action):
        """
        Corrected _max_action_length for the indenting of subactions.

        Plagiarized from stackoverflow.com

        This allows better formatting of the sdk help
        """
        if action.help is not SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent

            for subaction in self._iter_indented_subactions(action):

                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length, action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    def _format_action_invocation(self, action):
        """
        Overrides how args get printed with -h. Remove 'unnecessary' text in the output.
        """

        # For positionals
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar

        # For optionals
        return ", ".join(action.option_strings)
