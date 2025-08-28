
import os
from datetime import datetime
import uuid

from r7_surcom_sdk.lib import SurcomSDKException, SurcomAPI, constants, sdk_helpers, sdk_config
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand


class ImportCommand(SurcomSDKSubCommand):
    """
    [help]
    Import Type data into {PRODUCT_NAME}
    ---

    [description]
    This command imports Type data into {PRODUCT_NAME}.

It can be used to import data from a file, a directory or from a Connector 'build' directory.

The data must be in JSON format and the Type must already be installed in {PRODUCT_NAME}
or the schema must be defined in the Connector.

The command will create a batch for the import and add the data to the batch.

Once all the data has been added, the batch will be finalized and the import will be started
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -c <path_connector>
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -f <path_to_json_file>
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -d <path_to_data_directory>
    ---
    """
    def __init__(self, types_parser):

        self.cmd_name = constants.CMD_DATA
        self.sub_cmd_name = constants.CMD_IMPORT

        cmd_docstr = self.__doc__.format(
            PLATFORM_NAME=constants.PLATFORM_NAME,
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

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)
        self.cmd_parser.add_argument(*Args.path_file.flag, **Args.path_file.kwargs)
        self.cmd_parser.add_argument(*Args.dir_data.flag, **Args.dir_data.kwargs)
        self.cmd_parser.add_argument(*Args.yes.flag, **Args.yes.kwargs)

    def _create_types(
        self,
        surcom_client: SurcomAPI,
        files: list,
        path_types_dir: str
    ):
        for f in files:
            type_name = os.path.splitext(os.path.basename(f))[0]

            sdk_helpers.print_log_msg(f"Ensuring we have the latest '{type_name}' installed")

            path_type_schema = os.path.join(path_types_dir, f"{type_name}.yaml")

            if not os.path.isfile(path_type_schema):
                raise SurcomSDKException(
                    f"Type schema file '{path_type_schema}' does not exist",
                    solution="Ensure you have provided a valid path to the connector directory with the -c flag"
                )

            type_schema_content = sdk_helpers.read_file(path_to_file=path_type_schema)

            surcom_client.types_create(content=type_schema_content)

            sdk_helpers.print_log_msg(f"Installed the latest '{type_name}' type in the {constants.PLATFORM_NAME}")

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(
            f"Importing data into {constants.PLATFORM_NAME}",
            divider=True
        )

        connection = sdk_config.get_default_connection(prompt=True, default_to_yes=args.yes)

        surcom_client = SurcomAPI(
            base_url=connection.url,
            api_key=connection.api_key,
            user_agent_str="import-data command"
        )

        # This will only have a value if we are in a connector directory
        path_types_dir = None

        if args.path_file:

            sdk_helpers.print_log_msg(
                f"Importing data from file: '{args.path_file}'"
            )

            if not os.path.isfile(args.path_file):
                raise SurcomSDKException(
                    f"File '{args.path_file}' does not exist. "
                    "Please provide a valid JSON file."
                )

            files = [os.path.abspath(args.path_file)]

        elif args.dir_data:

            sdk_helpers.print_log_msg(
                f"Importing data from directory: '{args.dir_data}'"
            )

            if not os.path.isdir(args.dir_data):
                raise SurcomSDKException(
                    f"Data directory '{args.dir_data}' does not exist. "
                    "Please provide a valid directory containing JSON files."
                )

            files = [os.path.join(args.dir_data, f) for f in os.listdir(args.dir_data)]

        else:
            path_connector = os.path.abspath(args.path_connector)
            path_build_dir = os.path.join(path_connector, constants.DIR_NAME_BUILD)
            path_types_dir = os.path.join(path_connector, constants.DIR_NAME_TYPES)
            path_data_dir = os.path.join(path_build_dir, constants.DIR_NAME_OUTPUT)

            sdk_helpers.print_log_msg(
                f"Importing data from the default build/output directory: '{path_data_dir}'"
            )

            if not os.path.isdir(path_data_dir):
                raise SurcomSDKException(
                    f"Data directory '{path_data_dir}' does not exist. "
                    f"Make sure the Connector at '{path_connector}' has been invoked first and returned valid results"
                )

            files = [os.path.join(path_data_dir, f) for f in os.listdir(path_data_dir)]

        # If there are files, ensure the types exist in Surface Command before importing
        if files and path_types_dir:
            self._create_types(
                surcom_client=surcom_client,
                files=files,
                path_types_dir=path_types_dir
            )

        types_to_import = []
        import_id = f"sys.surcom.sdk.import.data.{datetime.now().isoformat()}"
        execution_id = uuid.uuid4()
        batch_id = None

        while files:

            # If there is no batch, create one
            if not batch_id:

                sdk_helpers.print_log_msg(
                    f"Creating batch for import with ID: '{import_id}'"
                )

                batch_id = surcom_client.import_batch_create(
                    import_id=import_id,
                    execution_id=execution_id
                )

                sdk_helpers.print_log_msg(
                    f"Created batch '{batch_id}'"
                )

            f = files[0]
            file_index_stopped_at = 0

            type_name = os.path.splitext(os.path.basename(f))[0]
            type_content = sdk_helpers.read_file(path_to_file=f)

            for i, t in enumerate(type_content, start=file_index_stopped_at):

                types_to_import.append({
                    "type": type_name,
                    "content": t
                })

                if len(types_to_import) == constants.MAX_TYPES_TO_IMPORT:
                    sdk_helpers.print_log_msg(
                        f"We hit our paging limit of {constants.MAX_TYPES_TO_IMPORT}. "
                        f"Adding '{len(types_to_import)}' items to batch '{batch_id}' for import"
                    )
                    surcom_client.import_batch_add_data(
                        import_id=import_id,
                        batch_id=batch_id,
                        data=types_to_import
                    )
                    file_index_stopped_at = i
                    types_to_import = []

                elif i == len(type_content) - 1:
                    files.pop(0)

        # Import the remaining type data
        if types_to_import:
            sdk_helpers.print_log_msg(
                f"Adding final {len(types_to_import)} items to batch '{batch_id}' for import"
            )
            surcom_client.import_batch_add_data(
                import_id=import_id,
                batch_id=batch_id,
                data=types_to_import
            )

        # Finalize the import
        sdk_helpers.print_log_msg(
            f"Finalizing import with ID: '{import_id}' and batch ID: '{batch_id}'"
        )
        surcom_client.import_batch_finalize(
            import_id=import_id,
            batch_id=batch_id
        )

        sdk_helpers.print_log_msg(f"The Execution ID for this batch workflow is '{execution_id}'")

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command. Navigate to "
                                  f"{constants.PRODUCT_NAME} to see the results!",
                                  divider=True)
