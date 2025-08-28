
import logging
import os
import re
from datetime import datetime
from typing import List, Tuple, Union

from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import Version

from r7_surcom_sdk.lib import JSONRefResolveError, constants, sdk_helpers
from r7_surcom_sdk.lib.connector import Connector

LOG = logging.getLogger(__name__)


def manifest_required_properties(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    missing_props = []

    for prop_name in constants.REQUIRED_MANIFEST_PROPERTIES:

        prop_value = manifest_data.get(prop_name)

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


def manifest_valid_category(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    categories = manifest_data.get("categories", [])

    for c in categories:
        if c not in constants.VALID_CATEGORIES:
            msg = f"'{c}' is not a valid category. {solution}"
            msg = msg.format(", ".join(constants.VALID_CATEGORIES))
            return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_valid_id(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    connector_id = manifest_data.get("id")

    len_connector_id = len(connector_id)

    # Validate the length
    if len_connector_id >= 30:
        msg = f"The `id` '{connector_id}' is '{len_connector_id}' characters. "
        msg = f"{msg} It must be less than 30 {solution}"
        return False, msg

    # Validate that the id only includes a-z and `.`
    valid_id_pattern = r'^[a-z.0-9]+$'
    if not bool(re.match(valid_id_pattern, connector_id)):
        msg = f"The `id` should be a dotted string consisting of lowercase letters and numbers 0-9. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_valid_icon(
    manifest_data: dict,
    path_connector: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    icon = manifest_data.get("icon")

    if not icon:
        msg = f"No value is specified for the `icon` property. {solution}"
        return False, msg

    path_icon = os.path.join(path_connector, icon)

    if not os.path.isfile(path_icon):
        msg = f"The icon file could not be found at: '{path_icon}'. {solution}"
        return False, msg

    icon_ext = os.path.splitext(path_icon)[1]

    if not icon_ext or icon_ext != ".svg":
        msg = f"The icon must be a `.svg` file. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_len_readme_section(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    readme_section = manifest_data.get("readme")

    if readme_section:
        len_readme_section = len(readme_section)

        if len_readme_section >= 2000:
            msg = f"The `readme` section is '{len_readme_section}' characters. {solution}"
            return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_readme_scalar_format(
    path_manifest_file: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    readme_scalar = sdk_helpers.get_scalar_style(path_manifest_file, "readme")

    if readme_scalar != constants.SCALAR_FOLDED:
        msg = f"The `readme` section is not denoted by the correct scalar. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_requirements_scalar_format(
    path_manifest_file: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    requirements_scalar = sdk_helpers.get_scalar_style(path_manifest_file, "requirements")

    if requirements_scalar != constants.SCALAR_LITERAL:
        msg = f"The `requirements` section is not denoted by the correct scalar. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_len_description_section(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    desc_section = manifest_data.get("description")

    len_readme_section = len(desc_section)

    if len_readme_section >= 500:
        msg = f"The `description` section is '{len_readme_section}' characters. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_environment_name_latest(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    environment_name = manifest_data.get("environment-name")

    if environment_name and environment_name != constants.ENV_NAME_NOETIC_FISSION_PY311:
        msg = f"'{environment_name}' is not valid. {solution}"
        msg = msg.format(constants.ENV_NAME_NOETIC_FISSION_PY311)
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_valid_settings(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:
    validation_result: Union[List, Tuple] = []

    try:
        settings = sdk_helpers.resolve_refs(
            refs=manifest_data.get("settings", []),
            document=manifest_data,
            key_name="name",
            skip_resolve_error=False
        )
    except JSONRefResolveError as err:
        msg = f"There is a reference in the manifest that could not be resolved. {err}"
        validation_result.append((False, msg))

    if settings:
        for k, s in settings.items():
            s_name = s.get("name")
            s_type = s.get("type")
            s_nullable = s.get("nullable", True)
            s_default = s.get("default")
            s_enum = s.get("enum")
            s_items = s.get("items", {})

            if not s_name:
                msg = "No `name` specified for this setting"
                validation_result.append((False, msg))
                continue

            if not s_type:
                msg = f"No `type` defined for {s_name}"
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
                if s_nullable is not False:
                    msg = f"{msg}. This should be a required setting"
                    msg = f"{msg}. To make a setting required the `nullable` property should be set to 'false'"
                    validation_result.append((False, msg))
                    continue

                # It should have a default
                if not isinstance(s_default, bool):
                    msg = f"{msg}. It must have a `default` property set to 'true' or 'false'"
                    validation_result.append((False, msg))
                    continue

            # If the setting has an enum and is required
            if (s_nullable is False and s_enum) or \
               (s_nullable is False and s_type == "array" and s_items.get("enum")):

                # ensure it has a valid default
                if not s_default:
                    msg = f"'{s_name}' is required, and has an `enum`. It and must have a `default` property too"
                    validation_result.append((False, msg))
                    continue

                # If its has a default and the value is a string ensure the value is
                # not a conjur secret reference
                if s_default and isinstance(s_default, str) and s_default.startswith("@"):
                    msg = f"'{s_name}' is required, has an `enum` property and its default value is a secret reference"
                    msg = f"{msg}. The value of the `default` property cannot start with '@'"
                    validation_result.append((False, msg))
                    continue

    return validation_result


def manifest_changelog_is_valid(
    manifest_data: dict,
    **kwargs
) -> Tuple[bool, str]:

    # must have date property, be in the format YYYY-MM-DD and be +/- 2 days
    changelog = manifest_data.get("changelog")

    if not isinstance(changelog, list):
        msg = "The `changelog` must be a list"
        return False, msg

    # Validate that all the changelog entries have different version numbers
    versions = set()
    for change in changelog:
        version = change.get("version")
        if version and version in versions:
            msg = f"The change version '{version}' appears more than once"
            return False, msg
        versions.add(version)

    latest_change = changelog[0]

    # Validate required properties in the latest changelog entry
    for prop_name in constants.REQUIRED_CHANGELOG_PROPERTIES:
        prop_value = latest_change.get(prop_name)

        if not prop_value:
            msg = f"`{prop_name}` is required in the changelog and has not been specified"
            return False, msg

    # Validate the version in the latest changelog entry
    latest_change_version = Version(latest_change.get("version"))
    connector_version = Version(manifest_data.get("version"))

    if latest_change_version != connector_version:
        msg = f"the changelog version '{latest_change_version}' must equal"
        msg = f"{msg} the connector version '{connector_version}'"
        return False, msg

    if latest_change_version.micro != 0:
        msg = f"the BUILD number of the version '{latest_change_version}' must be '0'"
        return False, msg

    # Validate the date in the latest changelog entry
    latest_change_date = latest_change.get("date")
    date_solution = f"Please specify a date in the format {constants.VALID_CHANGELOG_DATE_FMT}"

    try:
        date_change = datetime.strptime(latest_change_date, "%Y-%m-%d")
    except ValueError:
        msg = f"'{latest_change_date}' is not a valid date. {date_solution}"
        return False, msg

    # A regex to check the format YYYY-MM-DD with leading zeroes for month/day
    valid_date_regex = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"

    if not re.match(valid_date_regex, latest_change_date):
        msg = f"'{latest_change_date}' is not a in the correct format. {date_solution}"
        return False, msg

    date_now = datetime.now()
    delta_days = abs((date_change.date() - date_now.date()).days)

    if delta_days > 5:
        msg = f"'{latest_change_date}' must be within 5 days from today '{date_now.date()}'"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_requirements_screenshots_are_valid(
    manifest_data: dict,
    path_connector: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    requirements = manifest_data.get("requirements", "")

    regex = constants.REGEX_SS_REFERENCES
    screenshot_references = re.findall(regex, requirements)

    if screenshot_references:

        # NOTE: sometimes the path can be `/docs` or `docs` or `.docs`
        # we handle those cases, horribly
        dir_docs = os.path.basename(os.path.dirname(screenshot_references[0]).replace(".", ""))

        for ss in screenshot_references:

            path_ss = os.path.join(path_connector, dir_docs, os.path.basename(ss))

            if not os.path.isfile(path_ss):
                msg = solution.format(ss, path_ss, os.path.basename(path_connector))
                return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_secrets_are_no_longer_used(
    manifest_data: dict,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:
    secrets = manifest_data.get("secrets", "")

    if secrets:
        msg = f"The `secrets` property is deprecated. {solution}"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_type_icons(
    manifest_data: dict,
    solution: str,
    path_connector: str,
    **kwargs
) -> Tuple[bool, str]:
    types = manifest_data.get("types", [])

    for t in types:

        icon = t.get("icon")
        t_id = t.get("id")

        if icon:

            path_icon = os.path.join(path_connector, icon)

            if not os.path.isfile(path_icon):
                msg = f"The icon for '{t_id}' could not be found at: '{path_icon}'. {solution}"
                return False, msg

            icon_ext = os.path.splitext(path_icon)[1]

            if not icon_ext or icon_ext != ".svg":
                msg = f"The icon must be a `.svg` file. {solution}"
                return False, msg

    return True, constants.DEFAULT_PASS_MSG


def manifest_valid_setting_default_types(
    manifest_data: dict,
    **kwargs
) -> Tuple[bool, str]:
    validation_result: Union[List, Tuple] = []

    settings = sdk_helpers.resolve_refs(
        refs=manifest_data.get("settings", []),
        document=manifest_data,
        key_name="name",
        skip_resolve_error=True
    )
    if not settings:
        return validation_result

    for s_name, s in settings.items():

        s_default = s.get("default")

        # Continue if a conjur secret reference
        if isinstance(s_default, str) and s_default.startswith("@"):
            continue

        if s_default is not None:
            s_type = s.get("type", None)

            if not s_type:
                msg = f"The setting '{s_name}' has a `default` and does not specify a `type`"
                validation_result.append((False, msg))
                continue

            python_type = constants.OPEN_API_TYPES_TO_PYTHON.get(s_type)

            if not isinstance(s_default, python_type):
                msg = f"The `default` for the setting '{s_name}' is a '{type(s_default).__name__}'"
                msg = f"{msg} but the schema says it is '{s_type}'. The `default` must be the"
                msg = f"{msg} same datatype as the schema"
                validation_result.append((False, msg))
                continue

    return validation_result


# This validation only runs if --is-ci flag is set
def manifest_valid_conjur_secret_ids(
    manifest_data: dict,
    solution: str,
    path_all_connectors_dir: str,
    **kwargs
) -> Tuple[bool, str]:

    validation_result: Union[List, Tuple] = []

    # Get this connector's conjur secret ids
    settings = manifest_data.get("settings", [])
    secrets = manifest_data.get("secrets", [])
    conjur_secret_ids = []

    if settings:
        settings = sdk_helpers.resolve_refs(
            refs=settings,
            document=manifest_data,
            key_name="name",
            skip_resolve_error=True
        )
        for setting_name in settings:
            if "." in setting_name:
                conjur_secret_ids.append(setting_name)

    elif secrets:
        for secret in secrets:
            secret_name = secret.get("id")
            if "." in secret_name:
                conjur_secret_ids.append(secret_name)

    else:
        return validation_result

    # NOTE: If there are no secrets with a `.` in the name, no need
    # to do any further validations as the name will get
    # the connector namespace prefixed when installed
    if not conjur_secret_ids:
        return validation_result

    this_connector = Connector(manifest_data=manifest_data)

    # Get all connectors
    all_connectors: set[Connector] = sdk_helpers.get_all_connectors(path_all_connectors_dir=path_all_connectors_dir)

    all_connectors.remove(this_connector)

    existing_conjur_secret_ids = set()

    LOG.debug("Getting Conjur Secret IDs from each Connector")

    for c in all_connectors:
        c_settings = c.manifest.get("settings", []) or c.conn_spec.get("settings", [])
        c_secrets = c.manifest.get("secrets", [])

        if c_settings:
            c_settings = sdk_helpers.resolve_refs(
                refs=c_settings,
                document=c.manifest or c.conn_spec,
                key_name="name",
                skip_resolve_error=True
            )
            for setting_name in c_settings:
                if "." in setting_name:
                    existing_conjur_secret_ids.add(setting_name)

        elif c_secrets:
            for secret in c_secrets:
                secret_name = secret.get("id", "")
                if "." in secret_name:
                    existing_conjur_secret_ids.add(secret_name)

        else:
            continue

    for conjur_secret_id in conjur_secret_ids:
        if conjur_secret_id in existing_conjur_secret_ids:
            msg = f"The secret reference for '{conjur_secret_id}' contains a `.` and"
            msg = f"{msg} is not unique. Ensure it is by prefixing the settings name with the Connectors namespace"
            msg = f"{msg}. See our Submission Guide for more. {solution}"
            validation_result.append((False, msg))

    return validation_result


def manifest_valid_function_parameters(
    manifest_data: dict,
    **kwargs
) -> Tuple[bool, str]:
    validation_result: Union[List, Tuple] = []
    functions = manifest_data.get("functions", [])

    settings = sdk_helpers.resolve_refs(
        refs=manifest_data.get("settings", []),
        document=manifest_data,
        key_name="name",
        skip_resolve_error=True
    )
    if not settings:
        # Connector uses old-style settings, skip this check
        return validation_result

    for f in functions:

        f_id = f.get("id")
        f_name = f.get("name")
        f_parameters = f.get("parameters", [])

        if not f_id:
            msg = "No `id` specified for this Function"
            validation_result.append((False, msg))
            continue

        if not f_name:
            msg = f"No `name` specified for '{f_id}'"
            validation_result.append((False, msg))
            continue

        for p in f_parameters:
            rp, rp_default = None, None

            ref = p.get("$ref", None)
            p_default = p.get("default", None)
            p_name = p.get("name", ref)
            secret = None

            if ref:
                try:
                    rp = sdk_helpers.resolve_ref(ref=ref, document=manifest_data)
                    rp_default = rp.get("default", None)
                except JSONRefResolveError as err:
                    msg = f"There is a reference in the manifest that could not be resolved. {err}"
                    validation_result.append((False, msg))
                    continue

            # If `default` on the parameter has a value
            if p_default is not None:

                # The default is a conjur secret reference
                if isinstance(p_default, str) and p_default.startswith("@"):

                    # Ensure the conjur secret reference exists
                    secret = sdk_helpers.get_valid_secret(
                        secret_reference=p_default,
                        connector_id=manifest_data.get("id"),
                        settings=settings
                    )

                    if not secret:
                        msg = f"The `default` for the parameter '{p_name}' in the Function '{f_name}' is a"
                        msg = f"{msg} secret reference. However the secret reference '{p_default}' does"
                        msg = f"{msg} not exist. See our Submission Guide for more"
                        validation_result.append((False, msg))
                        continue

            # If `default` on the reference has a value
            if rp_default is not None:

                # The default is a conjur secret reference
                if isinstance(rp_default, str) and rp_default.startswith("@"):

                    # Ensure there is no default on the parameter default
                    if p_default is not None:
                        msg = f"The `default` for the function parameter at '{p_name}' is a secret"
                        msg = f"{msg} reference. There should be no `default` on the function parameter as well"
                        validation_result.append((False, msg))
                        continue

                    # Ensure the conjur secret reference exists
                    secret = sdk_helpers.get_valid_secret(
                        secret_reference=rp_default,
                        connector_id=manifest_data.get("id"),
                        settings=settings
                    )

                    if not secret:
                        msg = f"The `default` for the parameter '{p_name}' in the Function '{f_name}' is a"
                        msg = f"{msg} secret reference. However the secret reference '{rp_default}' does"
                        msg = f"{msg} not exist. See our Submission Guide for more"
                        validation_result.append((False, msg))
                        continue

                # The default is something else, make sure the function parameter has a valid secret reference
                else:
                    if p_default is None or (isinstance(p_default, str) and not p_default.startswith("@")):
                        msg = f"The '{p_name}' parameter in the Function '{f_name}' is a reference to a setting"
                        msg = f"{msg} that has an actual default, but the function parameter does not specify"
                        msg = f"{msg} a valid secret reference. See our Submission Guide for more"
                        validation_result.append((False, msg))
                        continue

            if secret and rp:
                secret_type = secret.get("type")
                rp_type = rp.get("type")

                if secret_type != rp_type:
                    msg = f"The setting `type` for '{secret.get('name')}' is '{secret_type}' and the function parameter"
                    msg = f"{msg} `type` for '{p_name}' is '{rp_type}'."
                    msg = f"{msg} The setting and function parameter MUST be the same type"
                    validation_result.append((False, msg))
                    continue

    return validation_result


def manifest_valid_function_returns_items(
    manifest_data: dict,
    **kwargs
) -> Tuple[bool, str]:

    validation_result: Union[List, Tuple] = []
    functions = manifest_data.get("functions", [])

    for fn in functions:
        fn_rtns = fn.get("returns", [])
        fn_name = fn.get("name", None)

        fn_rtns = sdk_helpers.resolve_refs(
            refs=fn.get("returns", []),
            document=manifest_data,
            key_name="name",
            skip_resolve_error=True
        )

        fn_rtn_items = bool(fn_rtns and fn_rtns.get("items", None))

        if not fn_rtn_items:
            continue

        if not fn.get(constants.FN_RTN_TYPES_PROP_NAME, None):
            msg = f"The function '{fn_name}' returns `items` however does not"
            msg = f"{msg} specify `{constants.FN_RTN_TYPES_PROP_NAME}`. Ensure this property exists for this function"
            msg = f"{msg} and that it is a list of all the Source Types this function returns"
            msg = f"{msg}. See our Submission Guide for more"
            validation_result.append((False, msg))
            continue

    return validation_result


def manifest_function_uses_more_data_correctly(
    manifest_data: dict,
    **kwargs
) -> Tuple[bool, str]:

    validation_result: Union[List, Tuple] = []
    functions = manifest_data.get("functions", [])
    key_param = "more_data"

    for fn in functions:
        fn_rtns = fn.get("returns", [])
        fn_name = fn.get("name", None)

        fn_rtns = sdk_helpers.resolve_refs(
            refs=fn.get("returns", []),
            document=manifest_data,
            key_name="name",
            skip_resolve_error=True
        )

        fn_rtn_has_more_data = bool(fn_rtns and fn_rtns.get(key_param, None))

        fn_params = sdk_helpers.resolve_refs(
            refs=fn.get("parameters", []),
            document=manifest_data,
            key_name="name",
            skip_resolve_error=True
        )

        fn_params_has_more_data = bool(fn_params and fn_params.get(key_param, None))

        if fn_rtn_has_more_data is False and fn_params_has_more_data is False:
            continue

        if fn_params_has_more_data is False:
            msg = f"The function '{fn_name}' returns `{key_param}` however does not"
            msg = f"{msg} specify `{key_param}` as an input parameter. Ensure `{key_param}` is"
            msg = f"{msg} also an input to this function"
            validation_result.append((False, msg))
            continue

        if fn_rtn_has_more_data is False:
            msg = f"The function '{fn_name}' has `{key_param}` as an input parameter however does not"
            msg = f"{msg} return it. Ensure this function also returns `{key_param}`"
            validation_result.append((False, msg))
            continue

    return validation_result


def requirements_txt_file_exists(
    path_connector: str,
    **kwargs
) -> Tuple[bool, str]:

    path_requirements_txt = os.path.join(path_connector, "requirements.txt")

    if not os.path.isfile(path_requirements_txt):
        msg = f"A valid 'requirements.txt' file was not found at '{path_requirements_txt}'"
        return False, msg

    return True, constants.DEFAULT_PASS_MSG


def requirements_txt_dep_is_valid(
    path_connector: str,
    solution: str,
    **kwargs
) -> Tuple[bool, str]:

    deps_to_skip = ["noetic_connector_api", "noetic-connector-api"]

    path_requirements_txt = os.path.join(path_connector, "requirements.txt")

    if not os.path.isfile(path_requirements_txt):
        msg = f"A valid 'requirements.txt' file was not found at '{path_requirements_txt}'"
        return False, msg

    with open(path_requirements_txt, "r", encoding=constants.ENCODING_UTF8_SIG) as f:
        requirements = f.readlines()

    requirements = sdk_helpers.read_file(path_requirements_txt, plain_text=True).splitlines()

    for r_str in requirements:
        r_str = r_str.strip()

        # Skip empty lines, comments and the noetic-connector-api dependency
        if not r_str or r_str.startswith("#") or r_str in deps_to_skip:
            continue

        # Skip dependencies that are a literal filename that exists in the connector
        if os.path.isfile(os.path.join(path_connector, r_str)):
            continue

        try:
            err_msg = f"The requirement '{r_str}' does not have a pinned version (e.g., '==1.0.0'). {solution}"
            r = Requirement(r_str)

            if not r.specifier:
                return False, err_msg

            for s in r.specifier:

                op = s.operator

                if op != "==":
                    return False, err_msg

        except InvalidRequirement as e:
            msg = f"Failed to parse the requirement '{r_str}': {e}"
            return False, msg

    return True, constants.DEFAULT_PASS_MSG
