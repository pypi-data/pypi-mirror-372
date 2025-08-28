import configparser
import logging
import os
import json
from typing import List
from urllib.parse import urlparse

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_terminal_fonts import fmt, formats

LOG = logging.getLogger(constants.LOGGER_NAME)


class SurcomSDKConfigConnection():

    def __init__(
        self,
        name: str,
        url: str,
        api_key: str,
        default: bool,
        resolve_1p_secrets: bool = True
    ):
        self.name = get_full_connection_name(name)
        self.original_url = url
        self.url = url
        self.default = default

        if resolve_1p_secrets:
            # This can also be <tenant>/<user>:<password>
            self.api_key = sdk_helpers.get_one_password_value(constants.CONFIG_NAME_API_KEY, api_key)
        else:
            self.api_key = api_key

        # NOTE: We handle the URL 'magically' here as it is simpler for the end user to
        # configure - all they have to do is copy the URL from the UI
        url = urlparse(self.url)
        scheme = url.scheme
        hostname = url.hostname

        if not hostname:
            hostname = url.path

        # Check if cluster is running locally
        if hostname in ["localhost", "127.0.0.1", "::1"]:
            self.url = "http://127.0.0.1"

        # Are we connecting to staging?
        elif "staging" in hostname:
            self.url = url.geturl()

        # Else we are connecting to a production instance
        else:
            if not scheme:
                scheme = "https"

            # NOTE: we assume the user has copied the URL from the UI so we get the API url
            if "surface" in hostname:
                # If the hostname contains 'surface', we replace it with 'api'
                hostname = hostname.replace("surface", "api")
                self.url = f"{scheme}://{hostname}/surface"

            else:
                self.url = f"{scheme}://{hostname}"

    def __str__(self):
        return f"Name:\t{self.name}\nURL:\t{self.url}"

    def __repr__(self):
        return self.__str__()


def get_full_connection_name(name: str) -> str:
    """
    :param name: name of the connection
    :type name: str
    :return: prefix `.connection` to the name if needed
        and return it
    :rtype: str
    """
    if not name.startswith(constants.CONFIG_SEC_CONN_PREFIX):
        name = f"{constants.CONFIG_SEC_CONN_PREFIX}.{name}"
    return name


def get_configs(
    path_config_file: str,
    section: str = None
) -> configparser.ConfigParser:
    """
    If a file exists in the correct format at `path_config_file`
    read the config from it and return a ConfigParser object

    If a `section` is provided, make sure it exists, but we always
    return the full ConfigParser object

    :param path_config_file: absolute path to the config file
    :type path_config_file: str
    :param section: if provided, make sure it exists, else we raise an error
    :type section: str, optional
    :return: all the configs in the config file as a ConfigParser object or
        else None if the file does not exist
    :rtype: ConfigParser
    """

    if not path_config_file:
        path_config_file = constants.PATH_SURCOM_CONFIG_FILE

    solution = f"Delete the file at '{path_config_file}' and run this command again"
    err_msg = "The config file is not in a format we expect"

    if not os.path.isfile(path_config_file):
        LOG.debug(f"No config file found at '{path_config_file}'")
        return None

    c = configparser.ConfigParser()

    try:
        c.read(path_config_file, encoding=constants.ENCODING_UTF8_SIG)
    except (
        configparser.MissingSectionHeaderError,
        configparser.ParsingError
    ):
        raise SurcomSDKException(message=err_msg, solution=solution)

    sections = c.sections()

    if not sections:
        raise SurcomSDKException(message=err_msg, solution=solution)

    for req_config in constants.REQ_CONFIGS:
        if not c.has_section(req_config[0]):
            raise SurcomSDKException(
                message=f"The config file does not specify the required section '{req_config[0]}'",
                solution=solution
            )

        if not c.has_option(section=req_config[0], option=req_config[1]):
            raise SurcomSDKException(
                message=f"The config file does not specify the required option '{req_config[1]}' "
                        f"in the section '{req_config[0]}'",
                solution=solution
            )

    if section and isinstance(section, str):
        if not c.has_section(section):

            raise SurcomSDKException(
                message=f"We could not find the section '{section}' in the config file at '{path_config_file}'"
            )

    return c


def get_config(
    option: str,
    section: str = constants.CONFIG_SEC_MAIN,
    option_type: str = "str",
    default: str = None,
) -> str:
    """
    Get the value of the given `option` in the given `section`
    from the config file at `constants.PATH_SURCOM_CONFIG_FILE`

    If the section or option does not exist, we raise a SurcomSDKException

    :param option: the option to get from the config file
    :type option: str
    :param section: the section to get the option from,
        defaults to `constants.CONFIG_SEC_MAIN`
    :type section: str, optional
    :param option_type: the type of the option, one of 'str', 'bool', 'int', 'float'
    :type option_type: str, optional
    :param default: if the option is not found, return this value instead, else we raise an error,
        defaults to None
    :type default: str, optional
    :return: the value of the option in the section
    :type section: str
    """

    configs = get_configs(path_config_file=constants.PATH_SURCOM_CONFIG_FILE)

    if not configs.has_section(section):
        raise SurcomSDKException(
            message=f"The config file does not specify the required section '{section}'",
            solution="Add this section to the config file"
        )

    if not configs.has_option(section=section, option=option):

        if default is not None:
            LOG.debug(f"We could not find the '{option}' option, so using the default value '{default}'")
            return default

        raise SurcomSDKException(
            message=f"The config file does not specify the required option '{option}' "
                    f"in the section '{section}'",
            solution="Add this option to the config file"
        )

    if option_type == "str":
        return configs.get(section=section, option=option)

    elif option_type == "bool":
        return configs.getboolean(section=section, option=option)

    elif option_type == "int":
        return configs.getint(section=section, option=option)

    elif option_type == "float":
        return configs.getfloat(section=section, option=option)

    else:
        raise SurcomSDKException(
            message=f"Unsupported option type '{option_type}' for the option '{option}' in the section '{section}'",
            solution="Use one of the supported types: 'str', 'bool', 'int', 'float'"
        )


def get_path_connector_dev(
    path_config_file: str = None
) -> str:
    """
    :param path_config_file: absolute path to the config file,
        defaults to constants.PATH_SURCOM_CONFIG_FILE
    :type path_config_file: str, optional
    :return: the value of `path_connector_ws` in the config file
    :rtype: str
    """

    # NOTE: we do this in here as if we set the default at the
    # function level our fx_use_tmp_test_path fixture does not interpolate
    # the paths correctly
    if not path_config_file:
        path_config_file = constants.PATH_SURCOM_CONFIG_FILE

    return get_config(option=constants.CONFIG_NAME_PATH_CONNECTOR_WS)


def get_connection_config(
    configs: configparser.ConfigParser,
    conn_name: str,
) -> SurcomSDKConfigConnection:
    """
    Get the given `conn_name` from the configs
    and return a SurcomSDKConfigConnection

    :param configs: the entire config file as a Configparser object
    :type configs: str
    :param conn_name: nickname or full section name of the connection
    :type conn_name: str
    :raises SurcomSDKException: if the Connection is not found or
        does not have all required config options
    :return: the Connection if found
    :rtype: SurcomSDKConfigConnection
    """
    conn_name = get_full_connection_name(conn_name)

    if not configs.has_section(conn_name):

        raise SurcomSDKException(
            message=f"We could not find any configuration for the connection '{conn_name}'",
            solution=f"Add this connection to the {constants.CONFIG_FILE_NAME} file by using the "
                     "`surcom config add` command"
        )

    for req_config in constants.REQ_CONNECTION_CONFIGS:
        if not configs.has_option(section=conn_name, option=req_config):
            raise SurcomSDKException(
                message=f"The '[{conn_name}]' does not specify the option '{req_config}'",
                solution="Add this option to the config"
            )

    config = SurcomSDKConfigConnection(
        name=conn_name,
        url=configs.get(section=conn_name, option=constants.CONFIG_NAME_URL),
        api_key=configs.get(section=conn_name, option=constants.CONFIG_NAME_API_KEY),
        default=configs.getboolean(section=conn_name, option=constants.CONFIG_NAME_ACTIVE)
    )

    return config


def delete_connection_config(
    configs: configparser.ConfigParser,
    conn_name: str
) -> None:
    """
    Delete the given `conn_name` from the configs

    :param configs: the entire config file as a Configparser object
    :type configs: configparser.ConfigParser
    :param conn_name: nickname or full section name of the connection
    :type conn_name: str
    """
    conn_name = get_full_connection_name(conn_name)

    if not configs.has_section(conn_name):
        raise SurcomSDKException(
            message=f"We could not find any configuration for the connection '{conn_name}'"
        )

    sdk_helpers.prompt_to_confirm(
        prompt=f"Are you sure you want to delete the connection '{conn_name}'?",
    )

    configs.remove_section(conn_name)

    write_config_file(config=configs)


def get_all_connections(
    path_config_file: str
) -> List[SurcomSDKConfigConnection]:
    """
    :param path_config_file: absolute path to the config file
    :type path_config_file: str
    :return: _description_
    :rtype: List[SurcomSDKConfigConnection]
    """
    rtn_list = []
    configs = get_configs(path_config_file=path_config_file)

    if not configs:
        return rtn_list

    for c in configs:
        if c.startswith(constants.CONFIG_SEC_CONN_PREFIX):
            rtn_list.append(get_connection_config(configs, c))

    return rtn_list


def update_defaults(
    configs: configparser.ConfigParser,
    new_default_conn: SurcomSDKConfigConnection
):
    """
    Loop through all the connections and mark the default property
    as `False`, except for the `new_default_conn`

    :param configs: the entire config file as a Configparser object
    :type configs: configparser.ConfigParser
    :param new_default_conn: new Connection that will be the default
    :type new_default_conn: SurcomSDKConfigConnection
    """
    if not configs:
        return

    for c in configs:
        if c.startswith(constants.CONFIG_SEC_CONN_PREFIX):
            conn = get_connection_config(configs, c)

            if conn.name != new_default_conn.name and conn.default:
                configs.set(conn.name, constants.CONFIG_NAME_ACTIVE, "False")

            elif conn.name == new_default_conn.name:
                configs.set(conn.name, constants.CONFIG_NAME_ACTIVE, "True")


def get_default_connection(
    path_config_file: str = None,
    prompt: bool = False,
    default_to_yes: bool = False
) -> SurcomSDKConfigConnection:
    """
    Get the first connection where `default` is `True`

    (There should only ever be one default. But we always get
    the first one anyway)

    :param path_config_file: absolute path to the config file
    :type path_config_file: str
    :return: the first connection in the config file where its
        `default` key is `True`
    :rtype: SurcomSDKConfigConnection
    """

    LOG.debug("Getting the Active Connection")

    c = get_configs(path_config_file=path_config_file)

    sections = c.sections()

    for s in sections:

        if s.startswith(constants.CONFIG_SEC_CONN_PREFIX):
            is_default = c.getboolean(section=s, option=constants.CONFIG_NAME_ACTIVE)

            if is_default:
                c = get_connection_config(configs=c, conn_name=s)

                # If we are prompted, we ask the user if they want to continue with this connection
                if prompt:

                    sdk_helpers.prompt_to_confirm(
                        prompt=f"The current Active Connection is '{c.name}' ({c.url})",
                        err_msg="You have chosen not to continue with the Active Connection",
                        err_solution="Select the connection you want to use by running "
                                     "`surcom config set-active` and then run this command again",
                        default_to_yes=default_to_yes
                    )

                return c

    raise SurcomSDKException(
        message="No active connection found",
        solution="Run `surcom config add-connection` to add one"
    )


def prompt_for_new_connection(initial_prompt: bool = False) -> SurcomSDKConfigConnection:
    """
    Prompt for;
        - Connection Name, which is the section name in the config
        - URL
        - API Key, which can be an actual API Key or a 1P Secret Reference
        - Default, input `y` or `n` if it's default key should be True or False

    Ensure the input matches the given `valid_regex_str`, else we prompt again for
    a max of 3 times until we error

    :return: the new Connection as a SurcomSDKConfigConnection object
    :rtype: SurcomSDKConfigConnection
    """
    url_prompt = f"\n{fmt(f'Enter the URL for the {constants.PLATFORM_NAME}', f=formats.BOLD)}"
    url = sdk_helpers.get_cli_input(
        prompt=url_prompt,
        valid_regex_str=r"^[a-z0-9.:/-]+$",
        default=constants.CONFIG_DEFAULT_URL
    )

    name_prompt = f"\n{fmt('Enter a Name for the connection (normally the name of your Organization)', f=formats.BOLD)}"
    name_prompt = f"{name_prompt}\nValid characters 'a-z, 0-9, -'"
    name = sdk_helpers.get_cli_input(
        prompt=name_prompt,
        valid_regex_str=r"^[a-z0-9-]+$"
    )

    api_key_prompt = f"\n{fmt('Enter a valid API Key or a 1Password Secret Reference', f=formats.BOLD)}"
    api_key = sdk_helpers.get_cli_input(
        prompt=api_key_prompt,
        is_password=True
    )

    if initial_prompt:
        default = "y"

    else:
        default_prompt = f"\n{fmt('Make Active? (y/n)', f=formats.BOLD)}"
        default = sdk_helpers.get_cli_input(
            prompt=default_prompt,
            default="y",
            valid_regex_str=r"^[yn]$"
        )
    default = True if default == "y" else False

    return SurcomSDKConfigConnection(
        name, url, api_key, default, resolve_1p_secrets=False
    )


def add_connector_settings(
    path_config_file: str,
    connector_id: str,
    settings: dict
):
    """
    Add the connector settings to the config file

    :param path_config_file: absolute path to the config file
    :type path_config_file: str
    :param connector_id: the connector id
    :type connector_id: str
    :param settings: the settings dict of the connector
    :type settings: dict
    """
    configs = get_configs(path_config_file=path_config_file)

    if not configs:
        raise SurcomSDKException(
            message="No config file found",
            solution="Run `surcom config init` to create one"
        )

    sdk_helpers.print_log_msg(
        f"Adding the settings for '{connector_id}' to the surcom config file",
    )

    section_name = f"{constants.CONFIG_SEC_CONNECTOR_PREFIX}.{connector_id}"

    if not configs.has_section(section_name):
        configs.add_section(section_name)

    else:
        sdk_helpers.print_log_msg(
            f"Section found for '{connector_id}', just updating"
        )

    for s_name, s in settings.items():

        if not configs.has_option(section_name, s_name):

            s_value = str(s.get("default", ""))

            if s.get("optional", False):
                s_name = f"-{s_name}"

            configs.set(section_name, s_name, s_value)

    write_config_file(config=configs)


def read_connector_settings(
    path_config_file: str,
    path_conn_spec: str,
    connector_id: str
) -> dict:
    """
    For each connector setting defined in the connector.spec.yaml file
    read its value from the surcom config file

    If the setting is not defined in the surcom config file, we add it to
    the return dict with a value of None

    If the setting starts with `-` in the surcom config we ignore it. This allows us
    to have optional settings in the config file, but not read them

    :param path_config_file: absolute path to the root config file of the surcom-sdk
    :type path_config_file: str
    :param path_conn_spec: absolute path to the connector.spec.yaml file of the connector
    :type path_conn_spec: str
    :param connector_id: the connector id
    :type connector_id: str
    :return: the settings dict of the connector
    :rtype: dict
    """

    configs = get_configs(path_config_file=path_config_file)
    connector_settings = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec).get("settings", {})
    settings = {s: None for s in connector_settings.keys()}

    if not configs:
        # TODO: make common
        raise SurcomSDKException(
            message="No config file found",
            solution="Run `surcom config init` to create one"
        )

    section_name = f"{constants.CONFIG_SEC_CONNECTOR_PREFIX}.{connector_id}"

    if not configs.has_section(section_name):
        raise SurcomSDKException(
            message=f"No settings found for '{connector_id}'",
            solution="Run `surcom connector codegen` to add them"
        )

    for s_name in configs.options(section_name):

        if s_name.startswith("-"):
            LOG.debug(f"Ignoring setting '{s_name[1:]}' as its prefix with '-'")
            continue

        connector_setting = connector_settings.get(s_name, {})

        s_type = connector_setting.get("type")

        if not connector_setting:
            sdk_helpers.print_log_msg(
                f"The setting '{s_name}' is not defined in the connector.spec.yaml file. We will assume it is a string",
                log_level=logging.WARNING,
            )
            s_type = "string"

        if s_type in ["string", "array"]:
            s = configs.get(section=section_name, option=s_name)
            settings[s_name] = sdk_helpers.get_one_password_value(config_name=s_name, config_value=s)
        elif s_type == "boolean":
            settings[s_name] = configs.getboolean(section=section_name, option=s_name)

        elif s_type == "integer":
            settings[s_name] = configs.getint(section=section_name, option=s_name)

        elif s_type == "number":
            settings[s_name] = configs.getfloat(section=section_name, option=s_name)

        elif s_type in ["object", "json"]:
            try:
                settings[s_name] = json.loads(configs.get(section=section_name, option=s_name))
            except json.JSONDecodeError:
                raise SurcomSDKException(
                    message=f"The setting '{s_name}' is not a valid JSON object",
                    solution="Ensure the setting is a valid JSON object"
                )
        else:
            raise SurcomSDKException(
                message=f"Unsupported type '{s_type}' for the setting '{s_name}'",
                solution="Enure the setting is one of the supported types: "
                        f"{', '.join(constants.PARAM_TYPE_MAP.keys())}"
            )

    return settings


def is_secret(name: str, settings: dict) -> bool:
    """
    Check if the setting has a format attribute and
    have the value of "password"

    :param name: the name of the setting
    :type name: str
    :param settings: all the settings for the connector in the connector.spec.yaml file
    :type settings: dict
    :return: True if the setting has a format attribute and its value is "password",
        False otherwise
    :rtype: bool
    """
    s = settings.get(name)

    if not s:
        return False

    return bool(s.get("format", "") == "password")


def write_config_file(
    config: configparser.ConfigParser
):
    """
    Write config to the default config file
    and create it if needed

    :param config: the full config object
    :type config: configparser.ConfigParser
    """

    if not os.path.exists(constants.PATH_SURCOM_ROOT):
        os.makedirs(constants.PATH_SURCOM_ROOT)

    with open(constants.PATH_SURCOM_CONFIG_FILE, mode="w", encoding=constants.ENCODING_UTF8) as fp:
        config.write(fp=fp)

    sdk_helpers.print_log_msg(f"Successfully wrote the updated config file to '{constants.PATH_SURCOM_CONFIG_FILE}'")
