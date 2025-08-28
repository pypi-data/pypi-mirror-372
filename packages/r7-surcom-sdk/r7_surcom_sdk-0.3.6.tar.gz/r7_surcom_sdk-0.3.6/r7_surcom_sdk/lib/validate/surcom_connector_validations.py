
from r7_surcom_sdk.lib import constants
from r7_surcom_sdk.cmds.connector.validate import Validation
from r7_surcom_sdk.lib.validate import legacy_connector_validate_fns as legacy_fns
from r7_surcom_sdk.lib.validate import surcom_connector_validate_fns as surcom_fns

VALIDATIONS = [
    ############################################################
    # We need these Validations to pass before we can continue #
    ############################################################
    Validation(
        title="required properties are set",
        fn=surcom_fns.required_properties,
        solution="Ensure the required properties '{0}' are all specified",
        level=constants.ISSUE_LEVEL_CRITICAL,
        fail_fast=True
    ),
    Validation(
        title="the `id` property",
        fn=legacy_fns.manifest_valid_id,
        solution="Please specify a valid `id`",
        level=constants.ISSUE_LEVEL_CRITICAL,
        fail_fast=True
    ),
    Validation(
        title="the settings are valid",
        fn=surcom_fns.valid_settings,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL,
        fail_fast=True
    ),

    Validation(
        title="all `categories` are valid",
        fn=legacy_fns.manifest_valid_category,
        solution="Please choose at least one of '{0}'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `version` property is valid",
        fn=surcom_fns.valid_version,
        solution="Ensure the `version` is a valid semantic version. E.g. '1.0.0'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="there is at least one entry for `current_changes`",
        fn=surcom_fns.valid_current_changes,
        solution="Ensure there is at least one entry in the `current_changes` list",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the `type` names are valid",
        fn=surcom_fns.valid_type_names,
        solution="Ensure all `type` names start with the Connector's prefix "
                 "to ensure uniqueness when installed",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each `type` definition exists",
        fn=surcom_fns.valid_type_definitions_exist,
        solution=f"Ensure all `type` definitions exist or update the {constants.CONN_SPEC_YAML} file "
                 "to remove the missing types",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="defines a test function",
        fn=surcom_fns.defines_test_function,
        solution="Each Connector must define a test function named 'test'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each function id is valid",
        fn=surcom_fns.valid_function_id,
        solution="Each function id must be snake_case containing only lowercase letters "
                 "and cannot start with 'fn_' or 'sc_'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each function python file exists",
        fn=surcom_fns.function_python_files_exist,
        solution="Each function must have a corresponding Python file in the 'functions' directory "
                 "where the file name is prefixed with 'fn_'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each function has valid return_types",
        fn=surcom_fns.valid_function_return_types,
        solution="Each function must have at least one valid type defined in its `return_types` list.",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="use a supported runtime",
        fn=surcom_fns.use_a_supported_runtime,
        solution="Ensure the `runtime` is one of the supported runtimes.",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="use the current default runtime",
        fn=surcom_fns.use_the_default_runtime,
        solution=f"We recommend using the latest supported runtime which is '{constants.DEFAULT_CURRENT_RUNTIME}'",
        level=constants.ISSUE_LEVEL_WARNING
    ),
    Validation(
        title="each setting has a description",
        fn=surcom_fns.settings_description_missing,
        solution="Ensure each setting has a description to help users understand its purpose",
        level=constants.ISSUE_LEVEL_WARNING
    ),
    Validation(
        title="the `settings` defaults have the correct types",
        fn=legacy_fns.manifest_valid_setting_default_types,
        solution=None,
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="each settings description is valid",
        fn=surcom_fns.valid_settings_description,
        solution="The description must be a string and can be a single line or if a multi-line string "
                 "it must use a folded scalar style with the last line removed: `>-`. "
                 "For example:\n\ndescription: >-\n   Enable this setting to import Users",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="there is an icon",
        fn=surcom_fns.valid_icon_file,
        solution="The Connector must have an icon file named 'icon.svg'",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the documentation is valid",
        fn=surcom_fns.docs_exist,
        solution="The Connector must have a documentation directory with a file named 'INSTRUCTIONS.md'. "
                 "There should be a separate section for Description, Overview and Documentation",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    Validation(
        title="the refdocs are valid",
        fn=surcom_fns.valid_ref_docs,
        solution="If the Connector has list of `reference-schemas`, each one must have a `file` and `url` property",
        level=constants.ISSUE_LEVEL_CRITICAL
    ),
    # TODO: validate the screenshots are PNGs and exist - there is legacy fn for this
    # TODO: validate there are no TODOs in any file
    # TODO: validate each dependency is pinned
]
