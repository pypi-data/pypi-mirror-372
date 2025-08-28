import configparser
import logging
import os
import shutil
import zipfile

from r7_surcom_sdk.cmds.data import ImportCommand
from r7_surcom_sdk.lib import (SurcomSDKException, constants, docker_helpers,
                               sdk_config, sdk_helpers)
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, formats

LOG = logging.getLogger(constants.LOGGER_NAME)


class InvokeCommand(SurcomSDKSubCommand):
    """
    [help]
    Invoke a Connector
    ---

    [description]
    This command allows you to invoke a Connector Function.

It builds a Docker image for the Connector and runs the Function in a Docker container.

Each Function in the Connector has access to all the Connector settings. Settings for
the Connector can be set in the {CONFIG_FILE_NAME} file, or passed as CLI arguments using the
`--settings` argument. 1Password Secret References can also be used in the {CONFIG_FILE_NAME} file.

A Function can be debugged by passing the `--debug` argument. This will expose the debug port
to allow remote debugging with a Python debugger like `debugpy`. See our documentation for
an example of how to do this with Visual Studio Code.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -f <some_function> --settings "severity=low"
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -f <some_function> --debug
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_INVOKE

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            COMMAND=self.cmd_name,
            CONFIG_FILE_NAME=constants.CONFIG_FILE_NAME,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.parent_parser = connectors_parser

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)
        self.cmd_parser.add_argument(*Args.path_connector_zip.flag, **Args.path_connector_zip.kwargs)
        self.cmd_parser.add_argument(*Args.fn_name.flag, **Args.fn_name.kwargs)
        self.cmd_parser.add_argument(Args.max_items.flag, **Args.max_items.kwargs)
        self.cmd_parser.add_argument(*Args.settings.flag, **Args.settings.kwargs)
        self.cmd_parser.add_argument(*Args.dir_output.flag, **Args.dir_output.kwargs)
        self.cmd_parser.add_argument(*Args.debug.flag, **Args.debug.kwargs)
        self.cmd_parser.add_argument(Args.no_cache.flag, **Args.no_cache.kwargs)
        self.cmd_parser.add_argument(Args.keep_build_files.flag, **Args.keep_build_files.kwargs)
        # TODO: add test for this flag
        self.cmd_parser.add_argument(Args.import_data.flag, **Args.import_data.kwargs)
        self.cmd_parser.add_argument(*Args.yes.flag, **Args.yes.kwargs)

    def _parse_cli_settings(
        self,
        args: str,
        existing_settings: dict
    ) -> dict:
        """
        Parse the CLI settings provided in the --settings argument and update the existing settings.

        :param settings_str: A string of settings in the format 'sname1=svalue1,sname2=svalue2'.
        :type settings_str: str
        :param existing_settings: The current settings dictionary to overwrite.
        :type existing_settings: dict
        :return: The updated settings dictionary.
        :rtype: dict
        """

        if not args.fn_settings:
            LOG.debug(f"No --settings provided, not overriding the {constants.CONFIG_FILE_NAME} settings")
            return existing_settings

        settings_str = args.fn_settings.replace(',', '\n')

        # Create a configparser object
        config = configparser.ConfigParser()

        # Wrap the settings string in a fake section header to make it parsable
        fake_section_name = "settings"
        fake_ini = f"[{fake_section_name}]\n{settings_str}"
        config.read_string(fake_ini)

        # Extract the parsed settings
        parsed_settings = dict(config[fake_section_name])

        # Overwrite the existing settings with the parsed ones
        existing_settings.update(parsed_settings)
        return existing_settings

    def _build_new_image(
        self,
        args,
        path_build_dir: str,
        path_docker_dir: str,
        path_docker_connector_package: str,
        connector_id: str,
        docker_tag: str,
        cmd_package,
    ):
        """
        Build a new Docker image for the Connector.
        This function handles the extraction of the Connector zip file, rendering the Dockerfile,
        and building the Docker image

        :param args: The command line arguments
        :type args: Argparse Namespace
        :param path_build_dir: The path to the build directory
        :type path_build_dir: str
        :param path_docker_dir: The path to the Docker directory
        :type path_docker_dir: str
        :param path_docker_connector_package: The path to the Docker connector package
        :type path_docker_connector_package: str
        :param connector_id: The ID of the Connector
        :type connector_id: str
        :param docker_tag: The Docker tag for the image
        :type docker_tag: str
        :param cmd_package: An instance of the package command
        :type cmd_package: Command
        :raises SurcomSDKException: If the Docker image build fails
        """
        path_connector_zip = args.path_connector_zip
        path_connector = args.path_connector
        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)

        # Read the connector spec file
        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)

        try:
            # Remove any existing containers and images
            docker_helpers.delete_containers(docker_tag=docker_tag)
            docker_helpers.delete_image(docker_tag=docker_tag)

            if not path_connector_zip:
                cmd_package.run(args=args)
                path_connector_zip = sdk_helpers.get_latest_connector_zip(path_dir=path_build_dir)

            if not zipfile.is_zipfile(path_connector_zip):
                raise SurcomSDKException(
                    message=f"'{path_connector_zip}' is not a valid zip file",
                    solution="Please run `surcom connector package` again to create a valid zip file",
                )

            # Ensure the Docker directory exists
            os.makedirs(path_docker_dir, exist_ok=True)

            # Extract the .zip file to the Docker directory
            with zipfile.ZipFile(path_connector_zip, "r") as zip_ref:
                zip_ref.extractall(path_docker_connector_package)

            template_data = conn_spec
            template_data["verbose"] = args.verbose

            # Check if we should use Artifactory for the r7-surcom-api
            use_artifactory = sdk_config.get_config(
                option=constants.CONFIG_NAME_USE_ARTIFACTORY,
                option_type="bool",
                default=False
            )

            if use_artifactory:
                template_data["use_artifactory"] = use_artifactory
                sdk_helpers.print_log_msg(
                    f"'{constants.CONFIG_NAME_USE_ARTIFACTORY}' is True. We will use Artifactory "
                    "to install the r7-surcom-api",
                    log_level=logging.WARNING
                )

            if args.debug:
                sdk_helpers.print_log_msg(
                    f"Debug mode enabled, exposing port {constants.DEBUG_PORT} for remote debugging",
                    log_level=logging.WARNING
                )
                template_data["debug_mode"] = True
                template_data["debug_port"] = constants.DEBUG_PORT

            dockerfile = sdk_helpers.render_jinja_template(
                template=constants.TEMPLATE_DOCKERFILE_SIMPLE,
                templates_path=constants.TEMPLATE_PATH_INVOKE,
                autoescape=False,
                data=template_data
            )

            sdk_helpers.write_file(
                path=os.path.join(path_docker_dir, constants.FILENAME_DOCKERFILE),
                contents=dockerfile.rendered_template
            )

            cli_args = ["docker", "build", "-t", docker_tag, path_docker_dir]

            if args.no_cache:
                cli_args.append("--no-cache")

            if args.verbose:
                cli_args.append("--progress=plain")

            sdk_helpers.print_log_msg(f"Building a new image for '{connector_id}'")

            sdk_helpers.run_subprocess(cli_args, capture_output=False)

            sdk_helpers.print_log_msg(
                f"Image built successfully: {docker_tag}",
                log_color=colors.OKGREEN,
                log_format=formats.BOLD
            )

        finally:
            if path_connector_zip and os.path.exists(path_connector_zip) and not args.keep_build_files:
                os.remove(path_connector_zip)

    def run(self, args, cmd_package):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg("Invoking a Connector", divider=True)

        # First, we check if the Docker CLI is installed
        try:
            docker_helpers.is_installed()
        except SurcomSDKException:
            raise SurcomSDKException(
                message="Docker is not installed",
                solution="Docker is required to run this command. Please install it and try again"
            )

        path_connector = os.path.abspath(args.path_connector)

        # Check if the connector directory is valid. Raise an exception if it is not.
        sdk_helpers.is_connector_directory(path=path_connector)

        path_build_dir = os.path.join(path_connector, constants.DIR_NAME_BUILD)
        path_docker_dir = os.path.join(path_build_dir, constants.DIR_NAME_DOCKER)
        path_docker_env_file = os.path.join(path_docker_dir, constants.TEMPLATE_ENV_FILE)
        path_docker_connector_package = os.path.join(path_docker_dir, constants.DIR_NAME_SURCOM_CONNECTOR)
        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)

        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)
        connector_id = conn_spec.get("id")
        docker_tag = f"{constants.FULL_PROGRAM_NAME}/{connector_id}:latest"

        # If the build/docker dir already exists, remove it
        if os.path.exists(path_docker_dir):
            shutil.rmtree(path_docker_dir)

        if not docker_helpers.does_image_exist(docker_tag=docker_tag):
            sdk_helpers.print_log_msg(
                f"No image could be found for '{docker_tag}', building a new one", log_level=logging.WARNING)

        if args.no_cache:
            sdk_helpers.print_log_msg(
                "--no-cache was provided, force building a new image", log_level=logging.WARNING)

        self._build_new_image(
            args=args,
            path_build_dir=path_build_dir,
            path_docker_dir=path_docker_dir,
            path_docker_connector_package=path_docker_connector_package,
            connector_id=connector_id,
            docker_tag=docker_tag,
            cmd_package=cmd_package
        )

        try:
            # If a function name is provided
            if args.fn_name:

                # Get the path to the output directory
                path_output = sdk_helpers.get_output_dir(
                    dir_output=args.dir_output,
                    default=os.path.join(path_build_dir, constants.DIR_NAME_OUTPUT)
                )

                os.makedirs(path_output, exist_ok=True)

                settings = sdk_config.read_connector_settings(
                    path_config_file=constants.PATH_SURCOM_CONFIG_FILE,
                    path_conn_spec=path_conn_spec,
                    connector_id=connector_id
                )

                params = {}
                secrets = {}

                # Set the main cli args
                cli_args = ["docker", "run", "-v", f"{path_output}:/app/output"]

                # If we are running in debug mode, we need to expose the debug port
                if args.debug:
                    cli_args.extend(["-p", f"{constants.DEBUG_PORT}:{constants.DEBUG_PORT}"])

                # For each setting
                for s_name, s_value in settings.items():

                    if s_value is not None:

                        # If the setting is a secret, we need to write it to a .env file
                        if sdk_config.is_secret(name=s_name, settings=conn_spec.get("settings")):
                            secrets.update({s_name: s_value})

                        # Else, we pass it as a parameter
                        else:
                            params.update({s_name: str(s_value)})

                if secrets:

                    env_file = sdk_helpers.render_jinja_template(
                        template=constants.TEMPLATE_ENV_FILE,
                        templates_path=constants.TEMPLATE_PATH_INVOKE,
                        secrets=secrets
                    )

                    sdk_helpers.write_file(
                        path=path_docker_env_file,
                        contents=env_file.rendered_template
                    )

                    # Add the --env-file flag to the cli
                    cli_args.extend(["--env-file", path_docker_env_file])

                # Add args needed to run surcom_function_cli

                cli_args.extend([docker_tag, "python"])

                # If we are running in debug mode, run the container with
                # debugpy to allow remote debugging
                if args.debug:
                    cli_args.extend([
                        "-m", "debugpy", "--listen", f"0.0.0.0:{constants.DEBUG_PORT}", "--wait-for-client"
                    ])

                cli_args.extend(["-m", "functions", args.fn_name])

                if args.max_items:
                    cli_args.extend(["--max-items", str(args.max_items)])

                if args.verbose:
                    cli_args.append("--verbose")

                params = self._parse_cli_settings(
                    args=args,
                    existing_settings=params
                )

                if params:
                    for p_name, p_value in params.items():
                        cli_args.append(f"--{p_name}")
                        cli_args.append(str(p_value))

                sdk_helpers.print_log_msg(
                    f"Invoking the Function '{args.fn_name}' in '{connector_id}'...",
                    divider=True
                )

                if args.debug:
                    sdk_helpers.print_log_msg(
                        "Debug mode enabled, waiting for debugger to attach",
                        log_level=logging.WARNING
                    )

                sdk_helpers.run_subprocess(cli_args, capture_output=False)

                sdk_helpers.print_log_msg("Function complete! Any output has been "
                                          f"written to '{path_output}'", divider=True)

                # If the output exists and is not empty, we can call the import-data command
                if args.import_data and os.path.exists(path_output) and os.listdir(path_output):
                    import_data_cmd = ImportCommand(self.parent_parser)
                    args.path_file = None
                    args.dir_data = None
                    import_data_cmd.run(args=args)

            else:
                sdk_helpers.print_log_msg(f"Invoking the Connector '{connector_id}' with no parameters", divider=True)
                cli_args = ["docker", "run", docker_tag]
                sdk_helpers.run_subprocess(cli_args, capture_output=False)
                sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)

        finally:
            docker_helpers.delete_containers(docker_tag=docker_tag)

            if os.path.exists(path_docker_dir) and not args.keep_build_files:
                shutil.rmtree(path_docker_dir)

            # If the docker env file exists
            if os.path.exists(path_docker_env_file):

                # Overwrite it with junk
                sdk_helpers.write_file(path_docker_env_file, "...")

                # Then delete it
                os.remove(path_docker_env_file)
