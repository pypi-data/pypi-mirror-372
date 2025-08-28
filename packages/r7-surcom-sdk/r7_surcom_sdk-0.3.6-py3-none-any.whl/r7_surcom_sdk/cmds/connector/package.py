import os
import shutil
import logging

from r7_surcom_sdk.lib import constants, sdk_helpers, SurcomSDKException, ExtLibraryAPI
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_argparse import Args

LOG = logging.getLogger(constants.LOGGER_NAME)


class PackageCommand(SurcomSDKSubCommand):
    """
    [help]
    Package a Connector for submission to the {PLATFORM_NAME} team
    ---

    [description]
    Package a Connector so that you can install it in the {PLATFORM_NAME}

This will generate a .zip file in the 'build' directory that we can then sign
and install in {PRODUCT_NAME}.
    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} -c <path_connector>
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_PACKAGE

        cmd_docstr = self.__doc__.format(
            PROGRAM_NAME=constants.PROGRAM_NAME,
            PLATFORM_NAME=constants.PLATFORM_NAME,
            PRODUCT_NAME=constants.PRODUCT_NAME,
            COMMAND=self.cmd_name,
            SUB_CMD=self.sub_cmd_name
        )

        super().__init__(
            parent=connectors_parser,
            cmd_name=self.sub_cmd_name,
            cmd_docstr=cmd_docstr)

        self.cmd_parser.add_argument(*Args.path_connector.flag, **Args.path_connector.kwargs)
        self.cmd_parser.add_argument(*Args.dir_output.flag, **Args.dir_output.kwargs)
        self.cmd_parser.add_argument(Args.keep_build_files.flag, **Args.keep_build_files.kwargs)

    def _render_manifest_yaml(
        self,
        conn_spec: dict,
        path_md_file: str
    ) -> sdk_helpers.RenderedConnectorTemplate:
        """
        :param conn_spec: contents of the connector.spec.yaml file
        :type conn_spec: dict
        :param path_md_file: path to the markdown file
        :type path_md_file: str
        :return: a RenderedConnectorTemplate of package/manifest.yaml template
        :rtype: RenderedConnectorTemplate
        """

        # Get the docs from the markdown file
        md = sdk_helpers.parse_docs_from_markdown_file(path_docs_file=path_md_file)

        # NOTE: a connector developer only needs to provide
        # the `current_changes` in the connector.spec.yaml file

        # Generate the current changelog entry
        changelog = [sdk_helpers.generate_changelog_entry(
            version=conn_spec.get("version"),
            changes=conn_spec.get("current_changes", [])
        )]

        # TODO: have way to get the older changes from the connector.spec.yaml file
        # If the connector.spec.yaml file has older changes, use them
        # to overwrite what is in the Extensions Library
        older_changes = []

        # Create an instance of the Extensions Library API
        el_client = ExtLibraryAPI()

        if el_client.is_enabled():

            LOG.debug("Using the Extensions Library API to get the connector version history")

            # If its enabled, get the version history
            version_history = el_client.get_connector_version_history(connector_id=conn_spec.get("id"))

            # Here we convert the version history into our noetic changelog format
            for v in version_history:
                older_changes.append(
                    sdk_helpers.generate_changelog_entry(
                        version=v.get("version", None),
                        changes=[v.get("changes")] if v.get("changes") else [],
                        date=v.get("date")
                    )
                )

        changelog.extend(older_changes)

        template_data = {
            "noetic_builtins_version": constants.NOETIC_BUILTINS_VERSION,
            "changelog": changelog,
        }

        template_data.update(conn_spec)

        template_data["environment_name"] = constants.RUNTIME_MAP.get(conn_spec.get("runtime"))

        template_data = template_data | md

        # NOTE: here we do not want to escape the jinja template
        # because we want to keep the markdown formatting
        return sdk_helpers.render_jinja_template(
            template=constants.MANIFEST_YAML,
            templates_path=constants.TEMPLATE_PATH_PACKAGE,
            data=template_data,
            autoescape=False
        )

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Packaging the connector at '{args.path_connector}'", divider=True)

        path_connector = os.path.abspath(args.path_connector)

        # Check if the connector directory is valid. Raise an exception if it is not.
        sdk_helpers.is_connector_directory(path=path_connector)

        path_conn_spec = os.path.join(path_connector, constants.CONN_SPEC_YAML)
        path_docs_dir = os.path.join(path_connector, constants.DIR_NAME_DOCS)
        path_build_dir = os.path.join(path_connector, constants.DIR_NAME_BUILD)
        path_output = sdk_helpers.get_output_dir(dir_output=args.dir_output, default=path_build_dir)
        path_connector_package = os.path.join(path_output, constants.DIR_NAME_SURCOM_CONNECTOR)

        # If the build/surcom_connector dir already exists, remove it
        if os.path.exists(path_connector_package):
            # NOTE: this is relatively safe to do because it will only
            # remove the directory if it is called constants.DIR_NAME_SURCOM_CONNECTOR
            shutil.rmtree(path_connector_package)

        # Because we call the command from other subcommands, there
        # is a chance that this may not be set
        keep_build_files = getattr(args, "keep_build_files", False)

        conn_spec = sdk_helpers.read_conn_spec(path_conn_spec=path_conn_spec)

        zip_file_name = f"{conn_spec.get('id').replace('.', '-')}-v{conn_spec.get('version')}"
        path_generated_zip = os.path.join(path_output, zip_file_name)

        manifest_yaml = self._render_manifest_yaml(
            conn_spec=conn_spec,
            path_md_file=os.path.join(path_docs_dir, constants.FILENAME_INSTRUCTIONS)
        )

        main_py = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_MAIN_PY,
            templates_path=constants.TEMPLATE_PATH_FUNCTIONS,
        )

        requirements_txt = sdk_helpers.render_jinja_template(
            template=constants.TEMPLATE_IMPORT_REQ_TXT,
            templates_path=constants.TEMPLATE_PATH_PACKAGE,
            data=conn_spec
        )

        try:
            # Write manifest.yaml
            sdk_helpers.write_file(
                path=os.path.join(path_connector_package, constants.MANIFEST_YAML),
                contents=manifest_yaml.rendered_template
            )

            #  Copy any screenshots if they exist
            if os.path.exists(path_docs_dir):
                sdk_helpers.copy_files_in_dir(
                    path_src_dir=path_docs_dir,
                    path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_DOCS),
                    file_exts=[".png"],
                )

            # Write requirements.txt
            sdk_helpers.write_file(
                path=os.path.join(path_connector_package, constants.TEMPLATE_IMPORT_REQ_TXT),
                contents=requirements_txt.rendered_template
            )

            # Copy icon.svg
            shutil.copy(
                src=os.path.join(path_connector, constants.FILENAME_ICON),
                dst=os.path.join(path_connector_package, constants.FILENAME_ICON)
            )

            # Copy types/
            sdk_helpers.copy_files_in_dir(
                path_src_dir=os.path.join(path_connector, constants.DIR_NAME_TYPES),
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_TYPES),
                file_exts=[".yaml"],
            )

            # Copy functions/
            sdk_helpers.copy_files_in_dir(
                path_src_dir=os.path.join(path_connector, constants.DIR_NAME_FNS),
                path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_FNS),
                file_exts=[".py"],
            )

            # Write __main__.py to functions/ dir
            sdk_helpers.write_file(
                path=os.path.join(path_connector_package, constants.DIR_NAME_FNS, constants.TEMPLATE_MAIN_PY),
                contents=main_py.rendered_template
            )

            # If a sample_data directory exists, copy it
            path_sample_data = os.path.join(path_connector, constants.DIR_NAME_SAMPLE_DATA)
            if os.path.exists(path_sample_data):
                sdk_helpers.copy_files_in_dir(
                    path_src_dir=path_sample_data,
                    path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_SAMPLE_DATA),
                    file_exts=[".json"]
                )

            # If a refdocs directory exists, copy it
            path_refdocs = os.path.join(path_connector, constants.DIR_NAME_REFDOCS)
            if os.path.exists(path_refdocs):
                sdk_helpers.copy_files_in_dir(
                    path_src_dir=path_refdocs,
                    path_dst_dir=os.path.join(path_connector_package, constants.DIR_NAME_REFDOCS),
                    file_exts=[".json", ".yaml", ".yml"]
                )

            # If an old .zip exists, force remove it to avoid caching issues
            if os.path.exists(f"{path_generated_zip}.zip"):
                os.remove(f"{path_generated_zip}.zip")

            # Make unsigned .zip
            shutil.make_archive(
                base_name=path_generated_zip,
                format="zip",
                root_dir=path_connector_package
            )
        except Exception as e:

            # There was a problem, remove the .zip if created
            if os.path.exists(f"{path_generated_zip}.zip") and not keep_build_files:
                # NOTE: this is relatively safe to do because it will only
                # remove the directory if it is called constants.DIR_NAME_SURCOM_CONNECTOR
                shutil.rmtree(f"{path_generated_zip}.zip")

            raise e

        finally:
            # Remove the build files, unless specified otherwise
            if os.path.exists(path_connector_package) and not keep_build_files:
                shutil.rmtree(path_connector_package)

        sdk_helpers.print_log_msg(f"A Connector package was created at '{path_generated_zip}.zip'")

        sdk_helpers.print_log_msg(f"Finished running the '{self.sub_cmd_name}' command", divider=True)
