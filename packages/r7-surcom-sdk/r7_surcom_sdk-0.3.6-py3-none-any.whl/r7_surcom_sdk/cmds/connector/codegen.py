import logging
import os
import shutil
from typing import List

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers, sdk_config
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class CodegenCommand(SurcomSDKSubCommand):
    """
    [help]
    Generate the boilerplate code for a Connector
    ---

    [description]
    Using details specified in the connector.spec.yaml file generate all the
boilerplate code that is required for developing a Connector.

Run this command from the directory where the connector.spec.yaml file is located
otherwise provide the `--path-connector` argument.

The generated code will be written to the directory where the connector.spec.yaml file is.

When you run `codegen`, the {CONFIG_FILE_NAME} file will be updated with the Connector's settings
that are defined in the connector.spec.yaml file. These can be modified later when you
`invoke` the Connector.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} --path-connector /path/to/connector
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_CODEGEN

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)

    def _render_types_py(
        self,
        conn_spec: dict
    ) -> sdk_helpers.RenderedConnectorTemplate:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :return: a RenderedConnectorTemplate of functions/types.py template or None
            if no types are found in the connector.spec.yaml file
        :rtype: str
        """
        config_types = conn_spec.get("types")
        template_types = []

        if not config_types:
            sdk_helpers.print_log_msg(
                f"No 'types' were found in the '{constants.CONN_SPEC_YAML}' file for this Connector",
                log_level=logging.WARNING
            )
            return None

        for t in config_types:
            template_types.append({
                "name": t
            })

        template_data = {
            "types": template_types
        }

        return sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_TYPES_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
            data=template_data
        )

    def _render_types_yaml(
        self,
        conn_spec: dict,
    ) -> List[sdk_helpers.RenderedConnectorTemplate]:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :return: a list of RenderedConnectorTemplate of the types/surcom_type.yaml template
            for each type found in the connector.spec.yaml file
        :rtype: List[RenderedConnectorTemplate]
        """
        config_types = conn_spec.get(constants.DIR_NAME_TYPES)
        rtn_list = []

        if not config_types:
            raise SurcomSDKException(
                f"No types were found in the '{constants.CONN_SPEC_YAML}' file. A Connector"
                "must have at least one type",
                solution=f"Add a Type to the 'types' section of the '{constants.CONN_SPEC_YAML}' file"
            )
        template_data = dict(conn_spec)

        for t in config_types:

            template_data.update({
                "type_name": t,
                "type_title": sdk_helpers.add_whitespace_before_caps(t)
            })

            filename = f"{t}.yaml"

            rtn_list.append(
                sdk_helpers.render_jinja_template(
                    template=constants.TEMPLATE_TYPES_YAML,
                    templates_path=constants.TEMPLATE_PATH_TYPES,
                    rendered_filename=filename,
                    data=template_data
                )
            )

        return rtn_list

    def _render_settings_py(
        self,
        conn_spec: dict
    ) -> sdk_helpers.RenderedConnectorTemplate:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :return: a RenderedConnectorTemplate of functions/settings.py template or None
            if no settings are found in the connector.spec.yaml file
        :rtype: str
        """
        settings = conn_spec.get("settings")

        if not settings:
            sdk_helpers.print_log_msg(
                f"No settings were found in the '{constants.CONN_SPEC_YAML}' file for this Connector",
                log_level=logging.WARNING
            )
            return None

        template_data = {
            "settings": settings
        }

        return sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_SETTINGS_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
            data=template_data
        )

    def _render_functions_py(
        self,
        conn_spec: dict,
        settings_py: sdk_helpers.RenderedConnectorTemplate,
        types_py: sdk_helpers.RenderedConnectorTemplate
    ) -> List[sdk_helpers.RenderedConnectorTemplate]:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :return: a list of RenderedConnectorTemplate of the functions/functions.py template
            for each function found in the connector.spec.yaml file
        :rtype: List[RenderedConnectorTemplate]
        """
        config_fns = conn_spec.get(constants.DIR_FUNCTIONS)
        rtn_list = []

        if not config_fns:
            raise SurcomSDKException(
                f"No functions were found in the '{constants.CONN_SPEC_YAML}' file. A Connector"
                "must have at least one function",
                solution=f"Add a Function to the 'functions' section of the '{constants.CONN_SPEC_YAML}' file"
            )

        for f in config_fns:

            fn_id = f.get("id")

            if not fn_id:
                raise SurcomSDKException(
                    "The function does not have an `id` property",
                    solution="Each function must have an `id` property and its value must be snake_case"
                )

            template_data = settings_py.template_data | types_py.template_data
            template_data["function"] = f
            template_data["client_prefix"] = sdk_helpers.get_prefix_from_id(conn_spec.get("id"))
            filename = f"fn_{fn_id}.py"

            if fn_id == "test":
                template_name = constants.TEMPLATE_TEST_FN_PY
            else:
                template_name = constants.TEMPLATE_IMPORT_FN_PY

            rtn_list.append(
                sdk_helpers.render_jinja_template(
                    template=template_name,
                    templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
                    rendered_filename=filename,
                    data=template_data
                )
            )

        return rtn_list

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Generating boilerplate code for '{args.path_connector}'", divider=True)

        path_connector = os.path.abspath(args.path_connector)

        # Check if the connector directory is valid. Raise an exception if it is not.
        sdk_helpers.is_connector_directory(path=path_connector)

        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)
        path_connector_functions = os.path.join(path_connector, constants.DIR_FUNCTIONS)
        path_connector_types = os.path.join(path_connector, constants.DIR_NAME_TYPES)
        path_connector_docs = os.path.join(path_connector, constants.DIR_NAME_DOCS)

        # Read the connector spec file
        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)

        # Render all the templates
        settings_py = self._render_settings_py(conn_spec=conn_spec)

        # NOTE: types_py is the file that creates the SurcomTypes
        types_py = self._render_types_py(conn_spec=conn_spec)

        # NOTE: types_yaml are the actual type definitions
        types_yaml = self._render_types_yaml(conn_spec=conn_spec)

        functions_py = self._render_functions_py(
            conn_spec=conn_spec,
            settings_py=settings_py,
            types_py=types_py)

        helpers_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_HELPERS_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
            data={
                "client_prefix": sdk_helpers.get_prefix_from_id(conn_spec.get("id"))
            }
        )

        init_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_INIT_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
            data={
                "functions": conn_spec.get("functions")
            }
        )

        icon_svg = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_ICON,
            templates_path=constants.TEMPLATE_PATH_CODEGEN,
        )

        instructions_md = sdk_helpers.render_jinja_template(
            template=constants.FILENAME_INSTRUCTIONS,
            templates_path=constants.TEMPLATE_PATH_DOCS,
        )

        # TODO: surround with try/except. If we fail to write one file, delete them all

        # Write the icon file if it does not exist
        path_icon = os.path.join(path_connector, constants.FILENAME_ICON)

        if os.path.exists(path_icon):
            LOG.debug(f"Icon '{path_icon}' already exists. Skipping...")

        else:
            sdk_helpers.write_file(
                path=path_icon,
                contents=icon_svg.rendered_template
            )

        # Write the __init__.py file
        sdk_helpers.write_file(
            path=os.path.join(path_connector_functions, constants.TEMPLATE_INIT_PY),
            contents=init_py.rendered_template
        )

        if conn_spec.get("settings"):
            # Write the sc_settings.py file
            sdk_helpers.write_file(
                path=os.path.join(path_connector_functions, constants.TEMPLATE_SETTINGS_PY),
                contents=settings_py.rendered_template
            )

            # If there are settings, add them to the surcom_config file
            sdk_config.add_connector_settings(
                path_config_file=constants.PATH_SURCOM_CONFIG_FILE,
                connector_id=conn_spec.get("id"),
                settings=conn_spec.get("settings")
            )

        # Write the sc_types.py file
        sdk_helpers.write_file(
            path=os.path.join(path_connector_functions, constants.TEMPLATE_TYPES_PY),
            contents=types_py.rendered_template
        )

        for t in types_yaml:

            path_type = os.path.join(path_connector_types, t.filename)

            if os.path.exists(path_type):
                LOG.debug(f"Type '{path_type}' already exists. Skipping...")
                continue

            # Write the type YAML file
            sdk_helpers.write_file(
                path=path_type,
                contents=t.rendered_template
            )

        for f in functions_py:

            path_fn = os.path.join(path_connector_functions, f.filename)

            if os.path.exists(path_fn):
                LOG.debug(f"Function '{path_fn}' already exists. Skipping...")
                continue

            # Write the function.py file
            sdk_helpers.write_file(
                path=path_fn,
                contents=f.rendered_template
            )

        # TODO: add test this file was created
        # If the helpers.py file does not exist, create it
        if not os.path.exists(os.path.join(path_connector_functions, constants.TEMPLATE_HELPERS_PY)):

            # Write the helpers.py file
            sdk_helpers.write_file(
                path=os.path.join(path_connector_functions, constants.TEMPLATE_HELPERS_PY),
                contents=helpers_py.rendered_template
            )

        # Write the docs directory if it does not exist
        if os.path.exists(path_connector_docs):
            LOG.debug(f"Docs directory '{path_connector_docs}' already exists. Not overwriting...")

        else:
            # Create docs dir and write the INSTRUCTIONS.md file
            sdk_helpers.write_file(
                path=os.path.join(path_connector_docs, constants.FILENAME_INSTRUCTIONS),
                contents=instructions_md.rendered_template
            )

            # Get path to the default screenshot
            path_default_screenshot = sdk_helpers.get_path_to_resource(
                package_name=f"{constants.PACKAGE_NAME}.data.cmds.connector.codegen.docs",
                resource_name="1.png"
            )

            # Copy the  default screenshot
            shutil.copy(
                src=path_default_screenshot,
                dst=os.path.join(path_connector_docs, "1.png")
            )

        sdk_helpers.print_log_msg(f"Created the base files for '{conn_spec.get('id')}' at '{path_connector}'")

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
