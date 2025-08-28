
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.cmds.connector.validate import Validation
from r7_surcom_sdk.lib.validate import legacy_connector_validate_fns as fn

VALIDATIONS = [
    Validation(
        title="required properties are set",
        fn=fn.manifest_required_properties,
        solution="Ensure the required properties '{0}' are all specified",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `categories` property",
        fn=fn.manifest_valid_category,
        solution="Please choose at least one of '{0}'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `id` property",
        fn=fn.manifest_valid_id,
        solution="Please specify a valid `id`",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `readme` section is < 2000 characters",
        fn=fn.manifest_len_readme_section,
        solution="The `readme` section should be a brief description of the connector in plain text "
                 "and < 2000 characters long. Please make it concise and add any extra detail to "
                 "the `requirements` section if needed",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `readme` is formatted correctly",
        fn=fn.manifest_readme_scalar_format,
        solution="It should be a scalar written with the folded style (denoted by '>'). "
                 "For example:\nreadme: >\n   This is an example",
        level=constants.ISSUE_LEVEL_WARNING
    ),
    Validation(
        title="the `requirements` section is formatted correctly",
        fn=fn.manifest_requirements_scalar_format,
        solution="It should be a scalar written with the literal style (denoted by '|'). "
                 "For example:\nrequirements: |\n   This is an example",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `description` section is < 500 characters",
        fn=fn.manifest_len_description_section,
        solution="The `description` section is more of an overview, a very small description "
                 "of the connector in plain text. Its contents appears on the content card in the Extension Library. "
                 "It must be < 500 characters long",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `environment-name` property is the latest",
        fn=fn.manifest_environment_name_latest,
        solution="Please use the latest environment '{0}'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the latest `changelog`",
        fn=fn.manifest_changelog_is_valid,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the screenshots in `requirements`",
        fn=fn.manifest_requirements_screenshots_are_valid,
        solution="'{0}' is not a valid reference to a screenshot. The absolute path is: '{1}'. "
                 "Ensure all screenshots are PNG files and in the '{2}/docs/' directory",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `icon` property",
        fn=fn.manifest_valid_icon,
        solution="Provide a valid Connector icon. It should be an SVG file and approved by our Design Team",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `settings` property",
        fn=fn.manifest_valid_settings,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the function `parameters`",
        fn=fn.manifest_valid_function_parameters,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title=f"if function returns `items` and `{constants.FN_RTN_TYPES_PROP_NAME}` is present",
        fn=fn.manifest_valid_function_returns_items,
        solution=f"The function returns `items`. You need to list the `{constants.FN_RTN_TYPES_PROP_NAME}` it returns",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `settings` defaults have the correct types",
        fn=fn.manifest_valid_setting_default_types,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `settings` property is preferred over `secrets`",
        fn=fn.manifest_secrets_are_no_longer_used,
        solution="Migrate this Connector to use the new OpenAPI settings format. "
                 "See our Submission Guide for details on how to declare settings correctly",
        level=constants.ISSUE_LEVEL_WARNING
    ),
    Validation(
        title="the `settings` or `secrets` ids are properly defined",
        fn=fn.manifest_valid_conjur_secret_ids,
        solution="The secret reference must be unique to all other connector secret ids",
        level=constants.ISSUE_LEVEL_CRITICAL,
        ci_only=True
    ),
    Validation(
        title="types have valid icons",
        fn=fn.manifest_type_icons,
        solution="If a type has an icon, the icon must be a valid SVG file",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="more_data defined correctly",
        fn=fn.manifest_function_uses_more_data_correctly,
        solution="If a function returns `more_data`, it must also define `more_data` as an input parameter",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="a valid requirements.txt file exists",
        fn=fn.requirements_txt_file_exists,
        solution="Ensure a 'requirements.txt' file exists at at a minimum specifies the `noetic_connector_api` package",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each dependency in requirements.txt is valid",
        fn=fn.requirements_txt_dep_is_valid,
        solution="Ensure a each dependency in 'requirements.txt' is pinned to a specific version",
        level=constants.ISSUE_LEVEL_CRITICAL
    )
]
