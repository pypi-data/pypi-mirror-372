import logging
from typing import List, Tuple, Union
import os

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_argparse import Args
from r7_surcom_sdk.lib.sdk_cmd import SurcomSDKSubCommand
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, fmt, formats


from r7_surcom_sdk.lib.validate.validation import Validation
from r7_surcom_sdk.lib.validate import legacy_connector_validations, surcom_connector_validations


LOG = logging.getLogger(constants.LOGGER_NAME)


class ValidateCommand(SurcomSDKSubCommand):
    """
    [help]
    Validate a Connector prior to submission
    ---

    [description]
    Once your Connector is ready, you can validate it using this command.

It will run a series of validations to ensure that the Connector meets the requirements for submission.

If any validations fail, it will provide solutions to fix them. All critical validations must
pass before you can submit the Connector.

    ---

    [usage]
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD}
    $ {PROGRAM_NAME} {COMMAND} {SUB_CMD} --skip-validations 'there is an icon' 'the documentation is valid'
    ---
    """
    def __init__(self, connectors_parser):

        self.cmd_name = constants.CMD_CONNECTORS
        self.sub_cmd_name = constants.CMD_VALIDATE

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
        self.cmd_parser.add_argument(Args.skip_validations.flag, **Args.skip_validations.kwargs)
        self.cmd_parser.add_argument(Args.multiple_connectors.flag, **Args.multiple_connectors.kwargs)
        self.cmd_parser.add_argument(Args.is_ci.flag, **Args.is_ci.kwargs)
        self.cmd_parser.add_argument(Args.path_all_connectors_dir.flag, **Args.path_all_connectors_dir.kwargs)

    def _handle_validation_result(
        self,
        validation: Validation,
        validation_result: Union[List, Tuple],
        critical_issues: List[Validation],
        warning_issues: List[Validation],
        info_issues: List[Validation]
    ):
        """
        If there is no validation_result, we do nothing and just return

        If there is a single validation_result, its a tuple and we update the issues list accordingly

        If there are multiple, its a list, we iterate and recursively call this fn

        :param validation: the Validation as configured in the configs.py file
        :type validation: Validation
        :param validation_result: the result after calling a method in the functions.py file
        :type validation_result: Union[List, Tuple]
        :param critical_issues: a list of all CRITICAL Validations
        :type critical_issues: List[Validation]
        :param warning_issues: a list of all WARNING Validations
        :type warning_issues: List[Validation]
        :param info_issues: a list of all INFO Validations
        :type info_issues: List[Validation]
        :raises ValueError: if the validation_result is not a list or a tuple
        """

        if not validation_result:
            # If no validations, we assume it passed
            return

        if isinstance(validation_result, tuple):
            is_valid, solution = validation_result

            if not is_valid:
                v = Validation(
                    title=validation.title,
                    fn=validation.fn,
                    solution=solution,
                    level=validation.level
                )

                if validation.level == constants.ISSUE_LEVEL_CRITICAL:
                    critical_issues.append(v)

                elif validation.level == constants.ISSUE_LEVEL_WARNING:
                    warning_issues.append(v)

                elif validation.level == constants.ISSUE_LEVEL_INFO:
                    info_issues.append(v)

        elif isinstance(validation_result, list):
            for r in validation_result:
                self._handle_validation_result(
                    validation=validation,
                    validation_result=r,
                    critical_issues=critical_issues,
                    warning_issues=warning_issues,
                    info_issues=info_issues
                )

        else:
            raise SurcomSDKException(
                "The 'validation_result' should be a Tuple or a List but"
                f"we got {type(validation_result)}"
            )

    def _run_validation(
        self,
        path_connector: str,
        validations: List[Validation],
        path_all_connectors_dir: str,
        is_ci: bool = False,
        **kwargs
    ) -> Tuple[List[Validation], List[Validation], List[Validation]]:
        """
        TODO
        """

        critical_issues: List[Validation] = []
        warning_issues: List[Validation] = []
        info_issues: List[Validation] = []

        if "manifest_data" not in kwargs:
            kwargs["manifest_data"] = kwargs.get("conn_spec_data", {})

        # Each validation could have 0 or more validation_results,
        # here we handle all cases
        for v in validations:

            if v.ci_only and not is_ci:
                sdk_helpers.print_log_msg(
                    f"Skipping validation '{v.title}' as it is marked for CI only. To run this validation, "
                    "enable CI mode with --is-ci.",
                    log_level=logging.DEBUG
                )
                continue

            LOG.debug(f"Running validation '{v.title}'")

            validation_result = v.fn(
                path_connector=path_connector,
                path_all_connectors_dir=path_all_connectors_dir,
                solution=v.solution,
                **kwargs
            )

            # As the issue lists are passed by reference, no need to explicitly return them here
            self._handle_validation_result(
                validation=v,
                validation_result=validation_result,
                critical_issues=critical_issues,
                warning_issues=warning_issues,
                info_issues=info_issues
            )

            if critical_issues and v.fail_fast:
                sdk_helpers.print_log_msg(
                    f"Critical issues found in the validation '{v.title}'. Stopping further validations. "
                    "It is required that these validations pass in order continue",
                    log_level=logging.ERROR
                )
                break

        return critical_issues, warning_issues, info_issues

    def run(self, args):
        SurcomSDKException.command_ran = f"{self.cmd_name} {self.sub_cmd_name}"

        sdk_helpers.print_log_msg(f"Starting the '{self.cmd_name} {self.sub_cmd_name}' command", divider=True)

        path_connectors_to_validate = [args.path_connector]

        if args.is_ci:
            sdk_helpers.print_log_msg(
                "Running in CI mode",
                log_level=logging.WARNING
            )

        if args.multiple_connectors:
            sdk_helpers.print_log_msg(
                f"Multiple connectors mode is enabled. Validating all connectors in '{args.path_connector}'",
                log_level=logging.WARNING
            )

            if not os.path.isdir(args.path_connector):
                raise SurcomSDKException(
                    f"The path '{args.path_connector}' is not a directory. "
                    "When using --multiple-connectors, the path must be a directory containing multiple connectors.",
                    solution="Ensure that each subfolder is a valid Connector with a connector.spec.yaml file."
                )

            path_connectors_to_validate = [
                os.path.join(args.path_connector, d)
                for d in os.listdir(args.path_connector)
                if os.path.isdir(os.path.join(args.path_connector, d))
            ]

            if not path_connectors_to_validate:
                raise SurcomSDKException(
                    f"No valid connectors found in the directory '{args.path_connector}'. "
                    "Ensure that each subfolder is a valid Connector with a connector.spec.yaml file.",
                    solution="Check the directory structure and ensure it contains valid connectors."
                )

        else:
            sdk_helpers.is_connector_directory(path=args.path_connector, raise_exception=True, legacy=True)

        critical_issues: List[Validation] = []
        warning_issues: List[Validation] = []
        info_issues: List[Validation] = []

        critical_str = f"{fmt('CRITICAL', c=colors.RED, f=formats.BOLD)}"
        fail_str = f"{fmt('FAILED VALIDATION', c=colors.RED, f=formats.BOLD)}"
        warning_str = f"{fmt('WARNING', c=colors.WARNING, f=formats.BOLD)}"
        info_str = f"{fmt('INFO', c=colors.BLUE, f=formats.BOLD)}"
        solution_str = f"{fmt('SOLUTION', f=formats.BOLD)}"
        skipped_str = f"{fmt('(SKIPPED)', c=colors.YELLOW, f=formats.BOLD)}"

        for path_connector in path_connectors_to_validate:

            if not sdk_helpers.is_connector_directory(path=path_connector, raise_exception=False, legacy=True):
                raise SurcomSDKException(
                    f"The path '{path_connector}' is not a valid Connector directory. "
                    "Ensure it contains a connector.spec.yaml file.",
                    solution="When using `--multiple-connectors`, each subfolder must be a valid Connector."
                )

            # If is Surcom Connector
            if sdk_helpers.is_surcom_or_legacy_connector(path_connector) == constants.SURCOM_CONNECTOR:

                sdk_helpers.print_log_msg(
                    f"Validating the Surcom Connector at: '{path_connector}'",
                    log_color=colors.BLUE
                )

                path_conn_spec_file = os.path.join(path_connector, constants.CONN_SPEC_YAML)

                criticals, warnings, infos = self._run_validation(
                    path_connector=path_connector,
                    validations=surcom_connector_validations.VALIDATIONS,
                    path_all_connectors_dir=args.path_all_connectors_dir,
                    is_ci=args.is_ci,
                    path_conn_spec_file=path_conn_spec_file,
                    conn_spec_data=sdk_helpers.read_file(path_to_file=path_conn_spec_file)
                )

                critical_issues.extend(criticals)
                warning_issues.extend(warnings)
                info_issues.extend(infos)

            # If is Legacy Connector
            elif sdk_helpers.is_surcom_or_legacy_connector(path_connector) == constants.LEGACY_CONNECTOR:

                sdk_helpers.print_log_msg(
                    f"Validating the Legacy Connector at: '{path_connector}'",
                    log_level=logging.WARNING
                )

                path_manifest_file = os.path.join(path_connector, constants.MANIFEST_YAML)

                criticals, warnings, infos = self._run_validation(
                    path_connector=path_connector,
                    validations=legacy_connector_validations.VALIDATIONS,
                    path_all_connectors_dir=args.path_all_connectors_dir,
                    is_ci=args.is_ci,
                    path_manifest_file=path_manifest_file,
                    manifest_data=sdk_helpers.read_file(path_to_file=path_manifest_file)
                )

                critical_issues.extend(criticals)
                warning_issues.extend(warnings)
                info_issues.extend(infos)

        # Print out any issues found
        for i in info_issues:
            msg = f"{info_str}: {i.title}"
            if i.solution:
                msg = f"{msg}\n      {i.solution}"
            sdk_helpers.print_log_msg(msg)

        for w in warning_issues:
            msg = f"{warning_str}: {w.title}"
            msg = f"{msg}\n{solution_str}: {w.solution}"
            sdk_helpers.print_log_msg(msg)

        for c in critical_issues:
            msg = f"{fail_str}: {c.title}"

            if c.title in args.skip_validations:
                c.skip = True

                msg = f"{msg} {skipped_str}"

            msg = f"{msg}\n{solution_str}: {c.solution}"
            sdk_helpers.print_log_msg(msg)

        # Print summary
        msg = "Validation completed with"
        msg = f"{msg} {fmt(len(critical_issues), c=colors.RED)} {critical_str} issue{'s'[:len(critical_issues)^1]},"
        msg = f"{msg} {fmt(len(warning_issues), c=colors.YELLOW)} {warning_str} level"
        msg = f"{msg} message{'s'[:len(warning_issues)^1]} and"
        msg = f"{msg} {fmt(len(info_issues), c=colors.BLUE)} {info_str} message{'s'[:len(info_issues)^1]}"
        sdk_helpers.print_log_msg(msg)

        # If all the critical issues are in skip validations, we just warn the user, else we raise an error
        if sdk_helpers.do_skip_validations(critical_issues):
            msg = f"Some {critical_str} issues did fail but they were"
            msg = f"{msg} marked as {skipped_str} because the `--skip-validations` flag was specified."
            msg = f"{msg}\nPlease ensure that the skipped validations are acceptable for your Connector."
            sdk_helpers.print_log_msg(msg)

            sdk_helpers.print_log_msg(
                "Validation completed successfully but some issues were skipped!",
                log_level=logging.WARNING,
                log_format=formats.BOLD
            )

        elif critical_issues:
            raise SurcomSDKException(
                f"There are {critical_str} issues that need to be resolved",
                solution="Please review the validation messages above and resolve the issues before proceeding."
            )

        else:
            sdk_helpers.print_log_msg(
                "Validation completed successfully!",
                log_color=colors.OKGREEN,
                log_format=formats.BOLD
            )

        sdk_helpers.print_log_msg(f"Finished running the '{self.cmd_name} {self.sub_cmd_name}' command", divider=True)
