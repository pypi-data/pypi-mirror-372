
"""
Module containing helper methods used throughout the r7_surcom_sdk
"""

import getpass
import glob
import json
import logging
import os
import re
import readline  # noqa
import shutil
import subprocess  # nosec: B404
from datetime import datetime
from importlib import metadata, resources
from typing import Any, List, Union

import yaml
from jinja2 import Environment, PackageLoader
from packaging.version import Version

from r7_surcom_sdk.lib import (JSONRefResolveError, SurcomSDKException,
                               constants)
from r7_surcom_sdk.lib.connector import ALL_CONNECTORS, Connector
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, fmt, formats
from r7_surcom_sdk.lib.validate.validation import Validation

# Get the same logger object that is used in main.py
LOG = logging.getLogger(constants.LOGGER_NAME)


class RenderedConnectorTemplate():
    """
    Class representing a Jinja template that has been
    rendered. It includes the filename, a dict of
    the data given to the template and
    a str of the rendered template
    """
    def __init__(
        self,
        filename: str,
        template_data: dict,
        rendered_template: str
    ):
        self.filename = filename
        self.template_data = template_data
        self.rendered_template = rendered_template

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.__str__()


def print_version():
    """
    Get the current version of the package and print a log
    """
    version = metadata.version(constants.PACKAGE_NAME)
    LOG.info(f"Installed version of the r7-surcom-sdk is: {version}")


def print_log_msg(
    log_msg: str,
    log_level=logging.INFO,
    divider=False,
    log_color: colors = None,
    log_format: formats = None
):
    """
    Log a message in yellow or red surrounded by the LOG_DIVIDER,
    depending on the logging level

    NOTE: If the NO_COLOR env var is set, no colors are added

    :param log_msg: the message to log out
    :type log_msg: str
    :param log_level: the level of the log, defaults to logging.INFO
    :type log_level: one of logging.INFO|DEBUG|WARNING|ERROR, optional
    :param divider: if True, adds the constants.LOG_DIVIDER. Defaults to False
    :type divider: bool, optional
    :param log_color: the color to use for the log message, defaults to None
    :type log_color: colors, optional
    :param log_format: the format to use for the log message, defaults to None
    :type log_format: formats, optional
    """

    log_color = log_color

    if log_level in (logging.DEBUG, logging.WARNING):
        log_color = colors.WARNING

    elif log_level == logging.ERROR:
        log_color = colors.FAIL

    if divider:
        log_msg = fmt(f"\n{constants.LOG_DIVIDER}\n{log_msg}\n{constants.LOG_DIVIDER}", c=log_color, f=log_format)

    else:
        log_msg = fmt(f"\n{log_msg}\n", c=log_color, f=log_format)

    LOG.log(level=log_level, msg=log_msg)


def read_file(
    path_to_file: str,
    plain_text: bool = False
) -> dict:
    """
    Read a file and return its contents as a dict.
    If the file is a JSON or YAML file, it will be parsed
    and returned as a dict

    :param path_to_file: path to the file to read
    :type path_to_file: str
    :param plain_text: if True, return the file contents as a plain text string,
        defaults to False
    :type plain_text: bool, optional
    :return: contents of the file as a dict
    :rtype: dict
    """
    content = {}

    if not os.path.isfile(path_to_file):
        raise SurcomSDKException(
            f"There is no file at '{path_to_file}'",
            solution="Ensure the file exists and try again"
        )

    ext = os.path.splitext(path_to_file)[1].lower()

    if not plain_text and ext == ".json":
        with open(path_to_file, "r", encoding=constants.ENCODING_UTF8_SIG) as fp:
            try:
                content = json.load(fp)
            except json.JSONDecodeError as e:
                raise SurcomSDKException(
                    message=f"Error reading JSON file '{path_to_file}': {str(e)}",
                    solution="Ensure the file is a valid JSON file and try again"
                )
    elif not plain_text and ext in (".yaml", ".yml"):
        with open(path_to_file, "r", encoding=constants.ENCODING_UTF8_SIG) as fp:
            try:
                content = yaml.safe_load(fp)
            except yaml.YAMLError as e:
                raise SurcomSDKException(
                    message=f"Error reading YAML file '{path_to_file}': {str(e)}",
                    solution="Ensure the file is a valid YAML file and try again"
                )
    else:
        with open(path_to_file, "r", encoding=constants.ENCODING_UTF8_SIG) as fp:
            content = fp.read()

    return content


def write_file(
    path: str,
    contents: str
):
    """
    Write `contents` to the file at `path`

    If the directory of `path` does not exist,
    create it

    :param path: absolute path to the file to write
    :type path: str
    :param contents: the contents to write to the file
    :type contents: str
    """
    base_dir = os.path.dirname(path)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    with open(path, mode="w", encoding=constants.ENCODING_UTF8) as fp:
        fp.write(contents)


def copy_files_in_dir(
    path_src_dir: str,
    path_dst_dir: str,
    file_exts: List[str] = None
):
    """
    Copy all files in the directory `path_src_dir` to `path_dst_dir`

    :param path_src_dir: path to the source directory
    :type path_src_dir: str
    :param path_dst_dir: path to the destination directory
    :type path_dst_dir: str
    :param ext: file extension to filter by, defaults to None
    :type ext: str, optional
    """

    if not os.path.isdir(path_src_dir):
        raise SurcomSDKException(
            f"There is no directory at '{path_src_dir}'. We cannot copy files",
            solution="Ensure the directory exists and try again"
        )

    if not os.path.exists(path_dst_dir):
        os.makedirs(path_dst_dir)

    for filename in os.listdir(path_src_dir):

        src_file = os.path.join(path_src_dir, filename)
        dst_file = os.path.join(path_dst_dir, filename)

        # If the file ext is not in the list of file_exts, skip it
        if file_exts and os.path.splitext(src_file)[1].lower() not in [ext.lower() for ext in file_exts]:
            continue

        if os.path.isfile(src_file):
            shutil.copy(src_file, dst_file)


def validate_conn_spec(
    conn_spec: dict
) -> bool:

    runtime = conn_spec.get("runtime")

    if runtime not in constants.RUNTIME_MAP.keys():
        raise SurcomSDKException(
            message=f"'{runtime}' is not a valid value for 'runtime'",
            solution="It must be a supported Python version. Supported "
                     f"versions are: '{','.join(constants.RUNTIME_MAP.keys())}'"
        )
    # TODO: a function id cannot be: test, settings or types


def read_conn_spec(
    path_conn_spec: str
) -> dict:
    """
    Read a connector.spec.yaml file and return its contents
    as a dictionary

    :param path_conn_spec: path to the connector.spec.yaml file to read
    :type path_conn_spec: str
    :return: contents of the file as a dictionary
    :rtype: dict
    """
    if not os.path.isfile(path_conn_spec):
        raise SurcomSDKException(
            f"There is no '{constants.CONN_SPEC_YAML}' file for the connector at '{path_conn_spec}'",
            solution="Check that you are in the connector's code directory"
        )

    with open(path_conn_spec, mode="r", encoding=constants.ENCODING_UTF8_SIG) as fp:
        conn_spec = yaml.safe_load(fp)

    validate_conn_spec(conn_spec=conn_spec)

    return conn_spec


def render_jinja_template(
    template: str,
    templates_path: str,
    rendered_filename: str = None,
    data: dict = None,
    autoescape: bool = True,
    *args,
    **kwargs
) -> RenderedConnectorTemplate:
    """
    Loads a Jinja template, renders it and returns a RenderedConnectorTemplate
    object. Passes on args and kwargs to the jinja render function

    :param template: the name of the template to render
    :type template: str
    :param templates_path: the path to the templates to load,
        normally something like 'data/cmds/connector'
    :type templates_path: str
    :param rendered_filename: name of the file rendered template. Defaults to the
        template name
    :type rendered_filename: str, optional
    :param data: a dict of data to pass to the template, defaults to None
    :type data: dict, optional
    :return: a rendered template
    :rtype: RenderedConnectorTemplate
    """
    if not data:
        data = {}

    if not rendered_filename:
        rendered_filename = template

    jinja_env = Environment(
        loader=PackageLoader(constants.PACKAGE_NAME, templates_path),
        # First newline after a block is removed
        trim_blocks=True,
        # Leading spaces and tabs are stripped from the start of a line to a block
        lstrip_blocks=True,
        # Preserve the trailing newline when rendering templates
        keep_trailing_newline=True,
        # Escape special characters to avoid XSS
        # NOTE: in most cases this is True, but to render the manifest.yaml file,
        # we mark this as False to preserve the markdown formatting
        autoescape=autoescape  # nosec: B701
    )

    jinja_env.filters["to_yaml"] = lambda value: yaml.dump(value, sort_keys=False)

    # Load the Jinja2 Template from template_name + jinja2 ext
    file_template = jinja_env.get_template(f"{template}.jinja2")

    kwargs.update({
        "data": data
    })

    # Render the template with the required variables
    rendered_template = file_template.render(*args, **kwargs)

    return RenderedConnectorTemplate(
        filename=rendered_filename,
        template_data=data,
        rendered_template=rendered_template
    )


def is_cli_input_valid(
    value: str,
    valid_regex_str: str
) -> bool:
    """
    :param value: value to validate
    :type value: str
    :param valid_regex_str: regex patten to validate against
    :type valid_regex_str: str
    :return: `True` if `value` matches the regex
        pattern `valid_regex_str`, else return `False`
    :rtype: bool
    """
    if not valid_regex_str:
        return True

    return bool(re.fullmatch(valid_regex_str, value))


def get_cli_input(
    prompt: str,
    default: Any = None,
    is_password: bool = False,
    valid_regex_str: str = None
) -> str:
    """
    Prompt the shell for the users input

    :param prompt: instructional text for the input
    :type prompt: str
    :param default: the default value to set this input to if the
        user just hits return, defaults to None
    :type default: Any, optional
    :param is_password: if set to `True` we use getpass to get the
        input so the secret value is not printed, defaults to False
    :type is_password: bool, optional
    :param valid_regex_str: a regex that that is validated against
        the input. If its invalid for 3 times, we raise a SurcomSDKException, defaults to None
    :type valid_regex_str: str, optional
    :return: the value of the user input
    :rtype: str
    """
    tries = 0

    if default:
        prompt = f"{prompt}\nDefaults to '{default}':\n> "

    else:
        prompt = f"{prompt}:\n> "

    if not is_password:

        v = input(prompt)

        if not v and default:
            return default

        while not is_cli_input_valid(value=v, valid_regex_str=valid_regex_str):

            tries = tries + 1

            if tries == constants.MAX_INPUT_TRIES:
                raise SurcomSDKException(
                    message=f"The user input of '{v}' is not valid",
                    solution=f"Ensure the input matches the given regex '{valid_regex_str}'"
                )

            v = input(prompt)

            if not v and default:
                return default

    else:
        v = getpass.getpass(prompt=prompt)

        while not v:

            tries = tries + 1

            if tries == constants.MAX_INPUT_TRIES:
                raise SurcomSDKException(message="You must supply a secret value")

            v = getpass.getpass(prompt=prompt)

    return v.strip()


def add_whitespace_before_caps(value: str) -> str:
    """
    Adds a whitespace before each uppercase letter in the given string.

    :param value: The input string that may contain uppercase letters.
    :type value: str
    :return: A new string with whitespace added before each uppercase letter.
    :rtype: str
    """
    if not value:
        return value

    return re.sub(r'([A-Z])', r' \1', value).strip()


def get_latest_connector_zip(
    path_dir: str
) -> str:
    """
    Get the latest .zip file in the given directory based on version in the filename

    :param path_dir: path to the directory to search
    :type path_dir: str
    :return: path to the latest .zip file
    :rtype: str
    """
    # Get all .zip files from the directory
    zip_files = glob.glob(os.path.join(path_dir, "*.zip"))

    if not zip_files:
        return None

    path_latest_connector_zip = None
    latest_version = None
    version_pattern = r"v(\d+\.\d+\.\d+)"

    for zip_file in zip_files:
        match = re.search(version_pattern, os.path.basename(zip_file))
        if match:
            current_version = Version(match.group(1))
            if latest_version is None or current_version > latest_version:
                latest_version = current_version
                path_latest_connector_zip = zip_file

    if not path_latest_connector_zip:
        return None

    return path_latest_connector_zip


def run_subprocess(cli_args: list, **kwargs):
    """
    Run a subprocess command with the given arguments.

    :param cli_args: The command and its arguments to run
    :type cli_args: list
    :param kwargs: Keyword arguments to be passed to subprocess.run.
    :type kwargs: dict
    :return: The result of the subprocess.run call.
    :rtype: subprocess.CompletedProcess
    """
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", True)

    cmd = " ".join(cli_args)

    LOG.debug(f"Running command: '{cmd}'")

    try:
        return subprocess.run(args=cli_args, **kwargs)  # nosec: B603
    except subprocess.CalledProcessError as e:

        LOG.debug(f"Error running command: '{cmd}'")
        LOG.debug(f"Command error: {str(e)}")

        stderr = getattr(e, 'stderr', None)

        if stderr:
            error_message = stderr.decode("utf-8").strip()

        else:
            error_message = str(e)

        raise SurcomSDKException(error_message)

    except Exception as e:
        raise SurcomSDKException(message=f"Error running command: '{cmd}'\nMessage: {str(e)}")


def get_path_to_resource(
    package_name: str,
    resource_name: str
) -> str:
    """
    Get the path to a file included in the Python package.

    :param package_name: The name of the package where the file is located
        Normally something like 'r7_surcom_sdk.data.deps'
    :type package_name: str
    :param resource_name: The name of the file to retrieve
    :type resource_name: str
    :return: The absolute path to the file.
    """
    with resources.as_file(resources.files(package_name).joinpath(resource_name)) as file_path:
        return str(file_path)


def is_one_password_value(config_value: str) -> bool:
    """
    Return True if config_value is a str and starts with "op://",
    else False

    :param config_value: the value of the config
    :type config_value: str
    :return: True if the given str starts with op://
    :rtype: bool
    """
    if isinstance(config_value, str) and config_value.startswith(constants.OP_PREFIX):
        return True

    return False


def get_one_password_value(config_name: str, config_value: str) -> str:
    """
    Check if the constants.ENV_OP_CLI is set

    Check if the constants.ENV_OP_CLI is a valid path

    If so, invoke the op CLI using a subprocess to get the value of the secret reference

    :param config_name: name of the config. Example: "password"
    :type config_name: str
    :param config_value: a valid 1Password secret reference.
        See https://developer.1password.com/docs/cli/secret-references for examples
    :type config_value: str
    :return: the actual value of the config returned from 1Password
    :rtype: str
    """

    # NOTE: Remove quotes from the `config_value` if they are present
    # This handles where the `config_value` is a 1Password Secret Reference copied directly from 1Password
    if config_value.startswith('"') and config_value.endswith('"'):
        config_value = config_value[1:-1]

    if not is_one_password_value(config_value):
        return config_value

    op = os.getenv(constants.ENV_OP_CLI)

    if not op:
        raise SurcomSDKException(
            f"The config '{config_name}' requires the environment variable '{constants.ENV_OP_CLI}' to be set",
            solution="Ensure you have the 1Password CLI installed and configured. See "
            "https://developer.1password.com/docs/cli/get-started/ for more information"
        )

    if not os.path.isfile(op):
        raise SurcomSDKException(
            f"'{constants.ENV_OP_CLI}' is invalid. It must be a valid path to a file: '{op}'")

    print_log_msg(f"Getting value in 1Password for '{config_name}' from: '{config_value}'")
    cli_args = [op, "read", config_value]
    result = run_subprocess(cli_args=cli_args)
    trimmed_result = result.stdout.decode("utf-8").strip()
    return trimmed_result


def parse_section_from_markdown(
    content: str,
    section: str
) -> str:
    """
    Parse a section from a markdown file and return the contents

    :param content: the content of the markdown file
    :type content: str
    :param section: the section to parse
    :type section: str
    :return: the contents of the section
    :rtype: str
    """
    regex = rf"# {section}\n(.*?)(?=\n# __|$)"

    match = re.search(regex, content, re.DOTALL)

    if match:
        return match.group(1).strip()

    return None


def parse_docs_from_markdown_file(
    path_docs_file: str
):
    """
    Parse the docs from a markdown file and return a dict
    of the contents

    :param path_docs_file: path to the markdown file to parse
    :type path_docs_file: str
    :return: a dict of the contents of the markdown file
    :rtype: dict
    """
    rtn_dict = {
        constants.MANIFEST_KEY_README: None,
        constants.MANIFEST_KEY_REQUIREMENTS: None
    }

    if not os.path.isfile(path_docs_file):
        raise SurcomSDKException(
            f"There is no file at '{path_docs_file}'",
            solution="Ensure the file exists and try again"
        )

    content = read_file(path_docs_file)

    md_description = parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_DESCRIPTION
    )

    if not md_description:
        raise SurcomSDKException(
            f"We could not find the {constants.MANIFEST_KEY_DESC} section in the file '{path_docs_file}'",
            solution=f"Ensure there is a '{constants.MANIFEST_KEY_DESC}' section and it is a valid markdown "
                     "file and try again"
        )

    rtn_dict[constants.MANIFEST_KEY_DESC] = md_description

    md_overview = parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_OVERVIEW
    )

    if not md_overview:
        raise SurcomSDKException(
            f"We could not find the {constants.MD_SECTION_OVERVIEW} section in the file '{path_docs_file}'",
            solution=f"Ensure there is a '{constants.MD_SECTION_OVERVIEW}' section and it is a valid markdown "
                     "file and try again"
        )

    # For each line break we add a double line break
    # to ensure it is rendered correctly in the Surface Command UI
    md_overview = md_overview.replace("\n\n", "\n\n\n")

    rtn_dict[constants.MANIFEST_KEY_README] = md_overview

    md_documentation = parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_DOCUMENTATION
    )

    # Remove the __Setup__ heading
    md_documentation = md_documentation.replace(f"## {constants.MD_SECTION_SETUP}\n\n", "").strip()

    # Find any screenshot references and prepend them with the path to the docs directory
    regex = constants.REGEX_SS_REFERENCES
    ss_refs = set(re.findall(regex, md_documentation))

    if ss_refs:
        for s in ss_refs:
            md_documentation = md_documentation.replace(s, f"{constants.DIR_NAME_DOCS}/{s}")

    rtn_dict[constants.MANIFEST_KEY_REQUIREMENTS] = md_documentation

    return rtn_dict


def generate_changelog_entry(
    version: str,
    changes: List[str],
    date: str = None
) -> dict:
    """
    Generate a changelog entry that is used in the manifest.yaml file

    :param version: The version number for the changelog entry.
    :type version: str
    :param changes: A list of changes made in this version.
    :type changes: List[str]
    :param date: The date of the release. If not provided, defaults
        to the current date.
    :type date: str, optional
    :return: A dictionary representing the changelog entry.
    :rtype: dict
    """

    if not date:
        date = datetime.now().strftime(constants.DATE_FORMAT_NOETIC)
    else:
        # NOTE: If there is a date, we assume we got it from the Extension Library
        # Because the Extension Library uses this format by default, we have to convert it back to
        # the format the manifest.yaml (a.k.a Noetic) needs
        date = datetime.strptime(date, constants.DATE_FORMAT_EXT_LIB).strftime(constants.DATE_FORMAT_NOETIC)

    # If its a single change and it contains a pipe character "|",
    # we got the change from the Extension Library and it contains multiple changes
    # so we split it on the pipe character
    if len(changes) == 1 and "|" in changes[0]:
        changes = changes[0].split("|")

    # Remove whitespace from each change
    changes = [c.strip() for c in changes if c]

    return {
        "version": version,
        "date": date,
        "text": changes
    }


def get_prefix_from_id(
    connector_id: str
) -> str:
    """
    Derive a prefix from the connector ID.

    Capitalizes each word in the ID and removes any dots, so that the ID
    "my.connector.id" becomes "MyConnectorId"

    :param connector_id: The connector ID to derive the prefix from
    :type connector_id: str
    :return: The prefix of the connector ID
    :rtype: str
    """
    if not connector_id:
        return ""

    return ''.join(word.capitalize() for word in connector_id.replace('.', ' ').split())


def clean_and_capitalize(s: str) -> str:
    """
    Clean a string by replacing certain characters with spaces,
    removing non-alphanumeric characters, and capitalizing the first letter of each word.
    This is useful for formatting names or titles in a more readable way.
    For example, "my.connector" becomes "My Connector".

    :param s: The input string to clean and capitalize
    :type s: str
    :return: The cleaned and capitalized string
    :rtype: str
    """
    if not s:
        return ""

    # Replace ., -, _ with spaces
    s = re.sub(r'[._-]', ' ', s)

    # Remove all non-alphanumeric characters except spaces
    s = re.sub(r'[^a-zA-Z0-9 ]+', '', s)

    # Lowercase everything, then capitalize the first character of each word
    return ' '.join(word.capitalize() for word in s.lower().split())


def is_connector_directory(
    path: str,
    raise_exception: bool = True,
    legacy: bool = False
) -> bool:
    """
    Check if the given path is a valid connector directory by checking
    if it contains a connector.spec.yaml file.

    If `legacy` is True, it also checks for the old manifest.yaml file.

    If `raise_exception` is True, it raises a SurcomSDKException
    if the path is not a valid connector directory.

    If `raise_exception` is False, it returns False if the path
    is not a valid connector directory, and True if it is.

    :param path: The path to check
    :type path: str
    :param raise_exception: If True, raises an exception if the path is not valid,
        defaults to True
    :type raise_exception: bool, optional
    :param legacy: If True, checks if a manifest.yaml file exists,
        defaults to False
    :type legacy: bool, optional
    :raises SurcomSDKException: If the path is not a valid connector directory
    :return: True if the path is a valid connector directory, False otherwise
    :rtype: bool
    """
    # Check if is a Surcom Connector
    is_connector_directory = bool(
        os.path.isdir(path) and os.path.isfile(os.path.join(path, constants.CONN_SPEC_YAML))
    )

    # If not a Surcom Connector and legacy is True, check for the old manifest.yaml file
    if legacy and not is_connector_directory:
        # If legacy is True, check for the old manifest.yaml file also
        is_connector_directory = bool(
            os.path.isdir(path) and os.path.isfile(os.path.join(path, constants.MANIFEST_YAML))
        )

    if not is_connector_directory:

        if raise_exception:
            raise SurcomSDKException(
                f"The path '{path}' is not a valid connector directory",
                solution="Ensure you have provided a valid path to the connector directory with the -c flag or "
                         "run this command again from a valid connector directory"
            )
        else:
            LOG.debug(f"The path '{path}' is not a valid Connector directory")
            return False

    return True


def make_backup(path_file: str):
    """
    Create a backup of the given file by appending the current timestamp to its name,
    then delete the original file.

    :param path_file: The path to the file to back up
    :type path_file: str
    """
    if not os.path.isfile(path_file):
        raise SurcomSDKException(f"Cannot create a backup for '{path_file}' because it does not exist")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path_file}.{timestamp}.bak"

    shutil.copy2(path_file, backup_path)

    os.remove(path_file)

    LOG.debug(f"Backup of '{path_file}' created at '{backup_path}'")

    return backup_path


def get_output_dir(
    dir_output: str,
    default: str
) -> str:
    """
    Get the output directory for the connector.

    If `dir_output` is not specified, use the default output directory.

    If `dir_output` is specified, check if it exists and is a directory.

    :param dir_output: The output directory specified by the user
    :type dir_output: str
    :param default: The default output directory to use if `dir_output` is not specified
    :type default: str
    :return: The output directory to use
    :rtype: str
    """

    if not dir_output:
        LOG.debug(f"No output directory specified, using default: '{default}'")
        os.makedirs(default, exist_ok=True)
        return default

    else:
        dir_output = os.path.abspath(dir_output)
        if not os.path.isdir(dir_output):
            raise SurcomSDKException(
                f"The output directory '{dir_output}' does not exist",
                solution="Ensure the directory exists and try again"
            )
        LOG.debug(f"Using specified output directory: '{dir_output}'")
        return dir_output


def prompt_to_confirm(
    prompt: str,
    err_msg: str = "User did not confirm the action",
    err_solution: str = "Ensure you want to continue and try again",
    default_to_yes: bool = False
):
    """
    Prompt the user to confirm an action with a yes/no question.

    :param prompt: The prompt message to display to the user
    :type prompt: str
    :param default: The default answer if the user just hits return.
        If set to "y", the default is yes, if set to "n", the default is no.
        Defaults to "y".
    :type default: str, optional
    :return: True if the user confirms, False otherwise
    :rtype: bool
    """
    str_prompt = f"{prompt}. Continue? (y/n)"
    usr_prompt = f"{fmt(str_prompt, f=formats.BOLD)}"

    if default_to_yes:

        print_log_msg(usr_prompt)

        print_log_msg(
            "Skipping prompt to confirm as '-y' flag was provided",
            log_level=logging.WARNING,
            log_format=formats.ITALIC
        )
        ans = "y"

    else:
        ans = get_cli_input(
            prompt=f"\n{usr_prompt}",
            default="y",
            valid_regex_str=r"^[yn]$"
        )

    yes = True if ans == "y" else False

    if not yes:
        raise SurcomSDKException(
            message=err_msg,
            solution=err_solution
        )


def get_user() -> str:
    """
    Get the current user of the system.

    :return: The current user
    :rtype: str
    """
    current_user = None

    try:
        current_user = getpass.getuser()
    except Exception:  # nosec: B110
        pass

    if not current_user:
        LOG.warning("Could not get the current user automatically")
        return None

    return current_user


def is_surcom_or_legacy_connector(
    path_connector: str
) -> str:
    """
    Check if the given path is a Surcom Connector or a legacy connector.

    A Surcom Connector is identified by the presence of a connector.spec.yaml file,
    while a legacy connector is identified by the presence of a manifest.yaml file.

    :param path_connector: The path to the connector directory
    :type path_connector: str
    :return: A string indicating the type of connector:
        - "SURCOM_CONNECTOR" if it is a Surcom Connector
        - "LEGACY_CONNECTOR" if it is a legacy connector
        - raises SurcomSDKException if neither file is found
    :rtype: str
    """

    is_connector_directory(
        path=path_connector,
        legacy=True
    )

    if os.path.isfile(os.path.join(path_connector, constants.CONN_SPEC_YAML)):
        return constants.SURCOM_CONNECTOR

    if os.path.isfile(os.path.join(path_connector, constants.MANIFEST_YAML)):
        return constants.LEGACY_CONNECTOR


def resolve_ref(ref: str, document: dict):
    """
    Resolves a $ref within the same document (local reference).
    Supports JSON Pointer style references

    :param ref: path to another part in the document
    :type ref: str
    :param document: the whole document containing the value of the
        reference
    :type document: dict
    :raises JSONRefResolveError: if the reference does not start with `#/`
    :raises JSONRefResolveError: if we fail to resolve the reference
    :return: the value of the reference
    :rtype: any
    """
    initial_chars = "#/"

    if not ref.startswith(initial_chars):
        raise JSONRefResolveError(f"Invalid JSON reference provided: '{ref}'")

    # Remove the initial '#/' and split the path by '/'
    parts = ref.lstrip(initial_chars).split("/")

    # Traverse the document based on the path
    ref_value = document
    for part in parts:
        ref_value = ref_value.get(part)
        if ref_value is None:
            raise JSONRefResolveError(f"Reference '{ref}' not found in the document.")

    return ref_value


def dict_to_list(
    obj: Union[list, dict],
    key_name: str
) -> dict:
    """
    Converts a dictionary to a list of dictionaries, where each dictionary
    in the list contains the original dictionary's key as a new property
    with the name `key_name`.

    If `obj` is already a list, it returns it as is.

    :param obj: The object to convert, can be a list or a dictionary.
    :type obj: Union[list, dict]
    :param key_name: The name of the new property to add to each dictionary.
    :type key_name: str
    :return: A list of dictionaries with the new property added.
    :rtype: list
    """
    rtn_list = []

    if isinstance(obj, list):
        return obj

    if isinstance(obj, dict):
        for k, v in obj.items():
            v.update({key_name: k})
            rtn_list.append(v)

    return rtn_list


def resolve_refs(
    refs: dict,
    document: dict,
    key_name: str,
    skip_resolve_error: bool = False
) -> dict:
    """
    Resolves multiple ref properties

    For each item in refs, check if there is a `$ref` property,
    and then check each one and if it is a JSON Reference, resolve it
    using document or else just add it as is and return a dict with the
    the value of <key_name> of each setting as the key

    :param refs: the refs to resolve
    :type refs: dict
    :param document: normally the contents of the manifest file
    :type document: dict
    :param key_name: the name of the property whose value we use in the return dict
    :type key_name: str
    :param skip_resolve_error: if True we do not raise an error when we fail
        to resolve, defaults to False
    :type skip_resolve_error: bool, optional
    :return: dict of each ref resolved
    :rtype: dict
    """
    resolved_refs = {}

    if not refs:
        return []

    for r in dict_to_list(refs, key_name=key_name):
        ref = r.get("$ref")

        if ref:
            try:
                r = resolve_ref(ref=ref, document=document)
            except JSONRefResolveError:
                if not skip_resolve_error:
                    raise

        resolved_refs.update({r.get(key_name): r})

    return resolved_refs


def do_skip_validations(
    validations: List[Validation],
    level: str = constants.ISSUE_LEVEL_CRITICAL
) -> bool:
    """
    If any Validation in the list has the same level and
    its skip value is marked as False, return False

    We only return True if all Validations
    of the given level are marked as skip=True

    :param validations: list of Validations
    :type validations: List[Validation]
    :param level: valid level of a Validation, defaults to constants.ISSUE_LEVEL_CRITICAL
    :type level: str, optional
    :return: True if all Validations of the given level are marked as skip=True,
        False if any Validation of the given level is marked as skip=False
    :rtype: bool
    """

    if not validations:
        return False

    skip = True

    for v in validations:

        if v.level == level:

            if v.skip is False:
                skip = False
                break

    return skip


def get_valid_secret(
    secret_reference: str,
    connector_id: str,
    settings: dict
) -> str:
    """
    There are multiple ways a conjur secret reference can be defined

    1. As is
    2. With the connectors namespace
    3. Without the connectors namespace (no this is different to 'As is' - don't ask)

    We use the `id` to get the namespace. A namespace is everything before the final `.`
    in the `id` property

    :param secret_reference: the conjur secret reference that starts with an `@`
    :type secret_reference: str
    :param connector_id: the id property in the manifest file
    :type connector_id: str
    :param settings: a dict of all settings. The output of the resolve_settings method
    :type settings: dict
    :return: the conjur secret if found, else None
    :rtype: None
    """
    if not settings:
        return None

    # Remove the @
    if secret_reference.startswith("@"):
        secret_reference = secret_reference[1:]

    the_setting = settings.get(secret_reference)

    if the_setting:
        return the_setting

    # Try getting setting when the namespace is prefix
    namespace = connector_id.rsplit(".", maxsplit=1)[0]
    namespaced = f"{namespace}.{secret_reference}"

    the_setting = settings.get(namespaced)

    if the_setting:
        return the_setting

    # Try getting setting when the namespace is removed from original
    if "." in secret_reference:
        removed_ns = secret_reference.replace(f"{namespace}.", "")
        the_setting = settings.get(removed_ns)

        if the_setting:
            return the_setting

    return None


def get_scalar_style(
    path_yaml_file: str,
    property_name: str,
    multiple: bool = False
):
    """
    Read a YAML file and determine the scalar style of the
    given property

    If the `property_name` is a nested property, we look for the parent
    property and then check the scalar style of the child property. For
    we just support one parent property, e.g. `settings.description`

    The scalar styles we check for are:
    - Folded scalar (>)
    - Literal scalar (|)
    - Folded scalar with last line removed (>-)

    :param path_yaml_file: the path to the YAML file
    :type path_yaml_file: str
    :param property_name: the name of the property to check
    :type property_name: str
    :return: the scalar style of the property, or None if not found
    :rtype: str | None
    """
    parent_found = True
    parent = None
    scalar_styles = []

    if "." in property_name:
        parent = f"{property_name.split('.')[0]}:"
        property_name = property_name.split(".")[1]
        parent_found = False

    with open(path_yaml_file, 'r', encoding=constants.ENCODING_UTF8_SIG) as f:
        for line in f:

            line = line.strip()

            if parent and parent in line:
                parent_found = True

            if not parent_found:
                continue

            # Detect folded scalar (>)
            m_folded = re.match(fr'^({property_name}+):\s*>\s*$', line)
            if m_folded:
                if multiple:
                    scalar_styles.append({property_name: constants.SCALAR_FOLDED})
                else:
                    return constants.SCALAR_FOLDED

            # Detect literal scalar (|)
            m_literal = re.match(fr'^({property_name}+):\s*\|\s*$', line)
            if m_literal:
                if multiple:
                    scalar_styles.append({property_name: constants.SCALAR_LITERAL})
                else:
                    return constants.SCALAR_LITERAL

            # Detect literal scalar with last line removed (|-)
            m_literal_chomped = re.match(fr'^({property_name}+):\s*\|\-\s*$', line)
            if m_literal_chomped:
                if multiple:
                    scalar_styles.append({property_name: constants.SCALAR_LITERAL_CHOMPED})
                else:
                    return constants.SCALAR_LITERAL_CHOMPED

            # Detect folded scalar with last line removed (>-)
            m_folded_chomped = re.match(fr'^({property_name}+):\s*\>\-\s*$', line)
            if m_folded_chomped:
                if multiple:
                    scalar_styles.append({property_name: constants.SCALAR_FOLDED_CHOMPED})
                else:
                    return constants.SCALAR_FOLDED_CHOMPED

    return scalar_styles if multiple else None


def has_files(
    path_dir: str
) -> bool:
    """
    Check if the given directory contains any files.

    :param path_dir: the path to the directory to check
    :type path_dir: str
    :return: True if the directory contains files, False otherwise
    :rtype: bool
    """
    return any(os.path.isfile(os.path.join(path_dir, f)) for f in os.listdir(path_dir))


def get_connector_src_paths(
    path_all_connectors_dir: str
) -> list:
    """
    Get all the absolute paths to all valid directories in the given path

    :param path_all_connectors_dir: path to a directory containing all connectors
    :type path_all_connectors_dir: str
    :return: a list of strings of absolute paths to connectors
    :rtype: list
    """
    src_paths = []

    LOG.debug(f"Getting all paths to source Connectors in '{path_all_connectors_dir}'")

    list_dir = os.listdir(path_all_connectors_dir)

    for src_app_dir_name in list_dir:

        if src_app_dir_name.startswith("__"):
            continue

        if src_app_dir_name.startswith("_"):
            continue

        if src_app_dir_name.startswith("."):
            continue

        if src_app_dir_name.startswith("pytest"):
            continue

        if src_app_dir_name in constants.DIRECTORIES_TO_IGNORE:
            continue

        path_src_app = os.path.join(path_all_connectors_dir, src_app_dir_name)

        if not os.path.isdir(path_src_app):
            continue

        if not has_files(path_src_app):
            continue

        src_paths.append(path_src_app)

    return sorted(src_paths)


def get_all_connectors(
    path_all_connectors_dir: str
) -> List[Connector]:
    """
    Given a path to a folder containing all connectors get each Connector by iterating over all the
    provided paths, attempting to open its connector.spec.yaml or manifest.yaml file and getting the details from it

    :param path_all_connectors_dir: path to a directory containing all connectors
    :type path_all_connectors_dir: str
    :return: all connectors found as a Python object
    :rtype: List[Connector]
    """

    # If Connectors are already read from disk, just return them
    if ALL_CONNECTORS:
        return ALL_CONNECTORS

    paths_connectors = get_connector_src_paths(path_all_connectors_dir)

    LOG.debug(f"Reading all {constants.CONN_SPEC_YAML} or {constants.MANIFEST_YAML} "
              f"files for each Connector in '{path_all_connectors_dir}'")

    # Else, we loop all the paths and read each connector
    for path_src in paths_connectors:

        manifest_data, conn_spec_data = None, None

        if is_surcom_or_legacy_connector(path_src) == constants.SURCOM_CONNECTOR:
            path_conn_spec = os.path.join(path_src, constants.CONN_SPEC_YAML)
            conn_spec_data = read_file(path_to_file=path_conn_spec)

        elif is_surcom_or_legacy_connector(path_src) == constants.LEGACY_CONNECTOR:

            path_manifest = os.path.join(path_src, constants.MANIFEST_YAML)
            manifest_data = read_file(path_to_file=path_manifest)

        if manifest_data or conn_spec_data:
            connector = Connector(
                manifest_data=manifest_data,
                conn_spec_data=conn_spec_data,
                path_src_code=path_src
            )

            ALL_CONNECTORS.add(connector)

    return ALL_CONNECTORS
