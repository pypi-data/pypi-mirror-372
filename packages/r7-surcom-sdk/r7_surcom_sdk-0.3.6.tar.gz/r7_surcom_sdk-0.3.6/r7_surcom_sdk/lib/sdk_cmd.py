
import re
from argparse import ArgumentParser, _SubParsersAction

from r7_surcom_sdk.lib import SurcomSDKException, constants
from r7_surcom_sdk.lib.sdk_argparse import (SurcomSDKArgHelpFormatter,
                                            SurcomSDKArgumentParser)
from r7_surcom_sdk.lib.sdk_terminal_fonts import fmt, formats


class SurcomSDKMainCommand(object):

    def __init__(
        self,
        parent: _SubParsersAction,
        cmd_name: str,
        cmd_docstr: str,
        include_sub_commands: bool = True
    ):
        """
        :param parent: the parent Argparse parser
        :type parent: _SubParsersAction
        :param cmd_name: name of the command
        :type cmd_name: str
        :param cmd_docstr: the docstr including help, description and usage. Normally `self.__doc__`
        :type cmd_docstr: str
        :param include_sub_commands: if `True` this command will have a sub group called `Commands`,
            else it does not. defaults to True
        :type include_sub_commands: bool, optional
        """
        cmd_args = SurcomSDKArgumentParser(
            prog=constants.PROGRAM_NAME,
            add_help=False,
            formatter_class=SurcomSDKArgHelpFormatter
        )

        if include_sub_commands:
            self.cmd_parser = cmd_args.add_subparsers(
                title=f"{fmt(constants.CMD_COMMANDS, f=formats.BOLD)}",
                metavar="",
                dest=cmd_name
            )

        surcom_cmd_docstr = SurcomCmdDocStr(cmd_name=cmd_name, cmd_docstr=cmd_docstr)

        self.main_parser: ArgumentParser = parent.add_parser(
            name=cmd_name,
            description=surcom_cmd_docstr.description,
            help=surcom_cmd_docstr.help,
            usage=surcom_cmd_docstr.usage,
            formatter_class=SurcomSDKArgHelpFormatter,
            parents=[cmd_args],
        )

    def run(self, args):
        """
        Implemented in a class that inherits this

        Takes the parsed args as an input
        """
        raise NotImplementedError()


class SurcomSDKSubCommand(object):
    """
    init/install/add
    """
    def __init__(
            self,
            parent,
            cmd_name,
            cmd_docstr: str = None
    ):
        """
        :param parent: the parent Argparse parser
        :type parent: _SubParsersAction
        :param cmd_name: name of the command
        :type cmd_name: str
        :param cmd_docstr: the docstr including help, description and usage. Normally `self.__doc__`
        :type cmd_docstr: str
        """

        surcom_cmd_docstr = SurcomCmdDocStr(cmd_name, cmd_docstr)

        self.cmd_parser: ArgumentParser = parent.add_parser(
            name=cmd_name,
            help=surcom_cmd_docstr.help,
            description=surcom_cmd_docstr.description,
            usage=surcom_cmd_docstr.usage,
            formatter_class=SurcomSDKArgHelpFormatter,
        )

    def run(self, args):
        """
        Implemented in a class that inherits this.

        Takes the parsed args as an input
        """
        raise NotImplementedError()


class SurcomCmdDocStr(object):

    def __init__(
            self,
            cmd_name: str,
            cmd_docstr: str
    ):
        """
        Parse the help, description and usage of a command if its in the format:

        ```
        [help]
        A summary of the command
        ---

        [description]
        A multiline long
        description
        ---

        [usage]
        $ {PROGRAM_NAME} {COMMAND} init -c <path_to_directory>
        ---
        ```

        :param cmd_name: Name of the command
        :type cmd_name: str
        :param cmd_docstr: The doc string of the command
        :type cmd_docstr: str
        """
        parsed_docstr = self.parse_docstr(cmd_name, cmd_docstr)

        self.help = parsed_docstr.get("help", "")
        self.description = parsed_docstr.get("description", "")
        self.usage = parsed_docstr.get("usage", "")

    def parse_docstr(
            self,
            cmd_name: str,
            cmd_docstr: str
    ) -> dict:
        """
        Parse the doc string of a command to extract the help, description and usage

        :param cmd_name: Name of the command
        :type cmd_name: str
        :param cmd_docstr: The doc string of the command
        :type cmd_docstr: str
        :return: A dictionary containing the help, description and usage
        :rtype: dict
        """
        # If no docstr is provided, just return an empty dict
        if not cmd_docstr:
            return {}

        regex = r"\[(.*?)\]\s*(.*?)\s*---"

        matches = re.findall(regex, cmd_docstr, re.DOTALL)

        if not matches or len(matches) != 3:
            raise SurcomSDKException(f"The doc string for '{cmd_name}' is invalid. Ensure it is in the format:\n"
                                     "[help]\na short summary\n---\n\n"
                                     "[description]\na multiline\ndescription\n---\n\n"
                                     "[usage]\n$ some examples how to use command\n---")

        return {
            "help": matches[0][1],
            "description": matches[1][1],
            "usage": f"\n    {matches[2][1]}"
        }
