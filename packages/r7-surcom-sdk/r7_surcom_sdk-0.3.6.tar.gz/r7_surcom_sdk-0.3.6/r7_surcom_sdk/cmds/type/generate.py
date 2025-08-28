

import os
import logging

from genson import SchemaBuilder

from r7_surcom_sdk.lib.sdk_terminal_fonts import formats
from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand

LOG = logging.getLogger(constants.LOGGER_NAME)


class GenerateCommand(SurcomSDKSubCommand):
    """
    [help]
    Generate a {PRODUCT_NAME} Type definition
    ---

    [description]
    Use this command to generate a draft Type definition for {PRODUCT_NAME} based on sample data.

It will read a JSON file containing data and generate a Type definition
based on the data in the file.

The Type definition will be written to a YAML file in the connector's types directory.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} <path_to_file>
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} build/output/Example.json
    ---
    """
    def __init__(self, types_parser):

        self.cmd_name = constants.CMD_TYPES
        self.sub_cmd_name = constants.CMD_GENERATE

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=types_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr
        )

        # TODO: support OpenAPI format
        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)
        self.cmd_parser.add_argument(Args.path_data_file.flag, **Args.path_data_file.kwargs)
        self.cmd_parser.add_argument(*Args.dir_output.flag, **Args.dir_output.kwargs)

    @staticmethod
    def _add_title_to_properties(properties: dict):
        """
        Add a title to each property if the property has a `type` key
        """
        if not properties:
            return {}

        for key, item in properties.items():

            if not item.get("type"):
                continue

            item["title"] = sdk_helpers.clean_and_capitalize(key)

        return properties

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Generating a Type Definition", divider=True)

        path_connector = os.path.abspath(args.path_connector)
        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)
        path_connector_types = os.path.join(path_connector, constants.DIR_NAME_TYPES)

        if not os.path.isfile(args.path_data_file):
            raise SurcomSDKException(
                f"We could not find a valid file at: '{args.path_data_file}'",
                solution="Ensure you have provided a valid path to the data file")

        # Check if the connector directory is valid. Raise an exception if it is not.
        sdk_helpers.is_connector_directory(path=path_connector)

        # Get the path to the output directory
        dir_output = sdk_helpers.get_output_dir(
            dir_output=args.dir_output,
            default=path_connector_types
        )

        # Read the connector spec file
        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)

        # Get the type data
        type_name = os.path.splitext(os.path.basename(args.path_data_file))[0]
        items = sdk_helpers.read_file(path_to_file=args.path_data_file)

        sdk_helpers.print_log_msg(f"Generating a skeleton type definition for '{type_name}' "
                                  f"from data in '{args.path_data_file}'", log_format=formats.BOLD)

        default_schema = {
            "x-samos-type-name": type_name,
            "x-samos-namespace": conn_spec.get("id"),
            "title": sdk_helpers.add_whitespace_before_caps(type_name),
            "description": "TODO Type Description",
            "x-samos-extends-types": [
                {
                    "type-name": "Machine",
                    "subtype-priority": 3
                }
            ],
            "x-samos-keys": [],
            "x-samos-table": [],
            "x-samos-detail": []
        }

        # Build the schema
        builder = SchemaBuilder()

        # Add each item to the schema builder
        for item in items:
            builder.add_object(item)

        # Get the schema from the builder
        schema = builder.to_schema()

        # We are just interested in the `properties` of the schema
        schema_props = schema.get("properties", {})

        schema_props = self._add_title_to_properties(properties=schema_props)

        # Get the keys from the schema properties
        schema_props_keys = schema_props.keys()

        # Keep track of the first key and first item
        first_key = list(schema_props_keys)[0]
        first_item = schema_props.get(first_key, {})

        # Add the first key to the `x-samos-keys`
        default_schema.get("x-samos-keys").append(first_key)

        # Add every top level property to the table and detail
        for prop in schema_props_keys:
            default_schema.get("x-samos-table").append(prop)
            default_schema.get("x-samos-detail").append(prop)

        # Add default values to the first item and make it fulfill core.component:id
        first_item["x-samos-immutable"] = True
        first_item["x-samos-fulfills"] = {}
        first_item["x-samos-fulfills"]["type-name"] = "core.component"
        first_item["x-samos-fulfills"]["property-name"] = "id"

        # Add schema properties to the default schema
        default_schema["properties"] = schema_props

        path_type_to_write = os.path.join(dir_output, f"{type_name}.yaml")

        sdk_helpers.print_log_msg(f"Writing the type definition to: '{path_type_to_write}'")

        type_yaml = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_TYPE_GENERATED_YAML,
            templates_path=constants.TEMPLATE_PATH_TYPES,
            data=default_schema
        )

        if os.path.isfile(path_type_to_write):
            sdk_helpers.print_log_msg(
                f"Type definition file '{path_type_to_write}' already exists. Renaming it with a `.bak` extension"
                " to avoid overwriting.",
                log_level=logging.WARNING
            )

            sdk_helpers.make_backup(path_file=path_type_to_write)

        sdk_helpers.write_file(
            path=path_type_to_write,
            contents=type_yaml.rendered_template
        )

        sdk_helpers.print_log_msg(f"Finished running the '{self.cmd_name} {self.sub_cmd_name}' command.", divider=True)
