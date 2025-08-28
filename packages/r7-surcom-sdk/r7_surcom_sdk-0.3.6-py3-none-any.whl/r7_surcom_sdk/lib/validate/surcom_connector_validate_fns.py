
import logging
import os
import re
from typing import List, Tuple, Union


from packaging.version import Version, InvalidVersion

from r7_surcom_sdk.lib import constants, sdk_helpers

LOG = logging.getLogger(__name__)


def required_properties(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    missing_props = []

    for prop_name in constants.REQUIRED_CONNECTOR_SPEC_PROPERTIES:

        prop_value = conn_spec_data.get(prop_name)

        if not prop_value:
            missing_props.append(prop_name)

    if missing_props:

        if len(missing_props) > 1:
            msg = f"`{', '.join(missing_props)}` are required and are not set"

        else:
            msg = f"`{', '.join(missing_props)}` is required and is not set"

        msg = f"{msg}. {solution}"

        msg = msg.format(", ".join(constants.REQUIRED_MANIFEST_PROPERTIES))

        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def valid_version(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    version_str = conn_spec_data.get("version")

    if not version_str:
        return False, f"The `version` property is required and is not set. {solution}"

    try:
        Version(version_str)
    except InvalidVersion as e:
        return False, f"The `version` property is not valid. {solution}. ERROR: {e}"

    return True, constants.DEFAULT_PASS_MSG


def valid_current_changes(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    current_changes = conn_spec_data.get("current_changes", [])

    if not current_changes:
        return False, f"{solution}. The `current_changes` property is required and is not set"

    if not isinstance(current_changes, list):
        return False, f"{solution}. The `current_changes` property must be a list"

    if len(current_changes) < 1:
        return False, f"{solution}. The `current_changes` property must have at least one entry"


def valid_type_names(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    types = conn_spec_data.get("types", [])

    if not types:
        return False, f"{solution}. The `types` property is required and is not set"

    prefix = sdk_helpers.get_prefix_from_id(conn_spec_data.get("id"))

    for t in types:
        if not t.startswith(prefix):
            msg = f"The type '{t}' is invalid. It must start with the Connector's prefix '{prefix}'. The"
            msg = f"{msg} prefix is derived from the Connector's `id` property. {solution}"
            validation_result.append((False, msg))

    return validation_result


def valid_type_definitions_exist(
    conn_spec_data: dict,
    path_connector: str,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    types = conn_spec_data.get("types", [])

    if not types:
        return False, f"{solution}. The `types` property is required and is not set"

    for t in types:

        path_type_def = os.path.join(path_connector, constants.DIR_NAME_TYPES, f"{t}.yaml")

        if not os.path.exists(path_type_def):
            msg = f"The type definition '{t}' is missing. It should be in the '{constants.DIR_NAME_TYPES}' directory"
            msg = f"{msg}. {solution}"
            validation_result.append((False, msg))

    return validation_result


def defines_test_function(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    functions = conn_spec_data.get("functions", [])

    if not functions:
        return False, f"{solution}. The `functions` property is required and is not set"

    for fn in functions:
        if fn.get("id") == constants.TEST_FN_ID:
            return True, constants.DEFAULT_PASS_MSG

    return False, f"{solution}. The `functions` property must list a function with id '{constants.TEST_FN_ID}'"


def valid_function_id(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    functions = conn_spec_data.get("functions", [])
    regex = r'^[a-z_]+$'

    if not functions:
        msg = f"{solution}. The functions property is required and is not set"
        validation_result.append((False, msg))
        return validation_result

    for fn in functions:

        fn_id = fn.get("id")

        if not fn_id:
            validation_result.append((False, f"{solution}. Each function must have an `id` property"))
            continue

        if not bool(re.fullmatch(regex, fn_id)):
            msg = f"The function id '{fn_id}' is invalid. {solution}"
            validation_result.append((False, msg))

        if fn_id.startswith("fn_") or fn_id.startswith("sc_"):
            msg = f"The function id '{fn_id}' is invalid. It must not start with 'fn_' or 'sc_'. {solution}"
            validation_result.append((False, msg))

    return validation_result


def function_python_files_exist(
    conn_spec_data: dict,
    path_connector: str,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    functions = conn_spec_data.get("functions", [])

    if not functions:
        msg = f"{solution}. The functions property is required and is not set"
        validation_result.append((False, msg))
        return validation_result

    for fn in functions:

        fn_id = fn.get("id")

        path_function_file = os.path.join(path_connector, constants.DIR_FUNCTIONS, f"fn_{fn_id}.py")

        if not os.path.exists(path_function_file):
            msg = f"Could not find a Python file for '{fn_id}'. It should be in the '{constants.DIR_FUNCTIONS}'"
            msg = f"{msg} directory. Run `codegen` to generate the function file. {solution}"
            validation_result.append((False, msg))

    return validation_result


def valid_function_return_types(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    functions = conn_spec_data.get("functions", [])
    types = conn_spec_data.get("types", [])

    for fn in functions:

        fn_id = fn.get("id")

        if fn_id == constants.TEST_FN_ID:
            continue  # Skip the test function

        fn_return_types = fn.get("return_types")

        if not fn_return_types:
            msg = f"The function '{fn_id}' is missing return_types. {solution}"
            validation_result.append((False, msg))
            continue

        for rt in fn_return_types:
            if rt not in types:
                msg = f"The return_type '{rt}' of function '{fn_id}' is not defined in the types. {solution}"
                validation_result.append((False, msg))

    return validation_result


def use_the_default_runtime(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    runtime = conn_spec_data.get("runtime")

    if runtime != constants.DEFAULT_CURRENT_RUNTIME:
        msg = f"The `runtime` property is set to '{runtime}'. {solution}."
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def use_a_supported_runtime(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    runtime = conn_spec_data.get("runtime")

    if runtime not in constants.SUPPORTED_RUNTIMES:
        return False, f"The `runtime` property must be one of '{constants.SUPPORTED_RUNTIMES}'. {solution}"

    return True, constants.DEFAULT_PASS_MSG


def settings_description_missing(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    settings = conn_spec_data.get("settings")

    for s_name, s in settings.items():

        if not s.get("description"):
            msg = f"The setting '{s_name}' is missing a description. {solution}"
            validation_result.append((False, msg))

    return validation_result


def valid_settings_description(
    path_conn_spec_file: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    scalars = sdk_helpers.get_scalar_style(path_conn_spec_file, "settings.description", multiple=True)

    if scalars:
        if not all(scalar_style.get("description") == constants.SCALAR_FOLDED_CHOMPED for scalar_style in scalars):
            return False, f"One of the settings descriptions uses an invalid scalar. {solution}"

    return True, constants.DEFAULT_PASS_MSG


def valid_settings(
    conn_spec_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    validation_result: Union[List, Tuple] = []

    settings = conn_spec_data.get("settings", {})

    for s_name, s in settings.items():
        s_title = s.get("title")
        s_type = s.get("type")
        s_nullable = s.get("nullable", False)
        s_default = s.get("default")
        s_enum = s.get("enum")

        # TODO: test an array setting with items that has an enum
        # s_items = s.get("items", {})

        # Has a title
        if not s_title:
            msg = f"No `title` specified for '{s_name}'. Each setting must have a `title` property"
            validation_result.append((False, msg))
            continue

        # Has a type
        if not s_type:
            msg = f"No `type` defined for '{s_name}'. Each setting must have a `type` property"
            validation_result.append((False, msg))
            continue

        # Valid type is used
        if s_type not in constants.VALID_SETTING_TYPES:
            valid_types_str = ", ".join(constants.VALID_SETTING_TYPES)
            msg = f"'{s_type}' is not a valid `type` for the setting '{s_name}'."
            msg = f"{msg} Please choose one of: {valid_types_str}"
            validation_result.append((False, msg))
            continue

        # If the setting is a boolean
        if s_type == "boolean":
            msg = f"'{s_name}' is a boolean"

            # It should be required
            if s_nullable is True:
                msg = f"{msg}. This should not be an optional setting"
                msg = f"{msg}. Remove the `nullable: true` property"
                validation_result.append((False, msg))
                continue

            # It should have a default
            if not isinstance(s_default, bool):
                msg = f"{msg}. It must have a `default` property set to 'true' or 'false'"
                validation_result.append((False, msg))
                continue

        # If its an array
        elif s_type == "array":
            # TODO: handle this
            msg = f"'{s_name}' is an array"
            continue

        # Else, if any other type and if the setting has an enum and is required
        elif s_nullable is False and s_enum:

            # ensure it has a default
            if not s_default:
                msg = f"'{s_name}' is required, and has an `enum`. It and must have a `default` property too"
                validation_result.append((False, msg))
                continue

            # If it has an enum, ensure the default is one of the enum values
            if s_default not in s_enum:
                msg = f"'{s_name}' is required, has an `enum` property and its default value '{s_default}'"
                msg = f"{msg} is not one of the enum values: {s_enum}"
                validation_result.append((False, msg))
                continue

    return validation_result


def valid_icon_file(
    path_connector: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    path_icon = os.path.join(path_connector, constants.FILENAME_ICON)

    if not os.path.isfile(path_icon):
        return False, f"The Connector icon file '{constants.FILENAME_ICON}' is missing. {solution}"

    return True, constants.DEFAULT_PASS_MSG


def docs_exist(
    path_connector: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    path_docs = os.path.join(path_connector, constants.DIR_NAME_DOCS)
    path_instructions = os.path.join(path_docs, constants.FILENAME_INSTRUCTIONS)
    regex_plain_text = r'^[A-Za-z0-9 .,;:!?\'"-()\\\n]+$'

    if not os.path.isdir(path_docs):
        return False, f"The Connector documentation directory '{constants.DIR_NAME_DOCS}' is missing. {solution}"

    if not os.path.isfile(path_instructions):
        return False, f"The Connector documentation file '{constants.FILENAME_INSTRUCTIONS}' is missing. {solution}"

    content = sdk_helpers.read_file(path_instructions)

    md_description = sdk_helpers.parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_DESCRIPTION
    )

    if not md_description:
        return False, f"The Description section is missing. {solution}"

    description_length = len(md_description)
    if description_length >= 150:
        msg = "The Description section is too long. It should be < 150"
        msg = f"{msg} characters and it is {description_length}. {solution}"
        return False, msg

    if "\n\n" in md_description:
        return False, f"The Description section must not contain any blank lines. {solution}"

    if not bool(re.fullmatch(regex_plain_text, md_description)):
        msg = "The Description section should be plain text only and must not contain any special formatting"
        solution = f"{msg}. {solution}"
        return False, msg

    md_overview = sdk_helpers.parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_OVERVIEW
    )

    overview_length = len(md_overview)
    if overview_length >= 2000:
        msg = "The Overview section is too long. It should be < 2000"
        msg = f"{msg} characters and it is {overview_length}. {solution}"
        return False, msg

    if not md_overview:
        return False, f"The Overview section is missing. {solution}"

    if not bool(re.fullmatch(regex_plain_text, md_overview)):
        msg = "The Overview section should be plain text only and must not contain any special formatting"
        solution = f"{msg}. {solution}"
        return False, msg

    md_documentation = sdk_helpers.parse_section_from_markdown(
        content=content,
        section=constants.MD_SECTION_DOCUMENTATION
    )

    if not md_documentation:
        return False, f"The Documentation section is missing. {solution}"

    return True, constants.DEFAULT_PASS_MSG


def valid_ref_docs(
    conn_spec_data: dict,
    path_connector: str,
    solution: str,
    **kwargs
) -> list:

    validation_result: Union[List, Tuple] = []

    ref_docs = conn_spec_data.get("reference-schemas", [])

    for ref_doc in ref_docs:
        if not ref_doc.get("url"):
            msg = f"The reference schema is missing a URL. {solution}"
            validation_result.append((False, msg))

        if not ref_doc.get("file"):
            msg = f"The reference schema is missing a file. {solution}"
            validation_result.append((False, msg))

        else:
            if not os.path.isfile(os.path.join(path_connector, ref_doc.get("file"))):
                msg = f"The reference schema file '{ref_doc.get('file')}' does not exist. {solution}"
                validation_result.append((False, msg))

    return validation_result
