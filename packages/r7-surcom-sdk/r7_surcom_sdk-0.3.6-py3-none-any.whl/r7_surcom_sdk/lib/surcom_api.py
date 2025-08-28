
import logging
import sys
from importlib.metadata import version

import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth

from r7_surcom_sdk.lib import SurcomSDKException, constants, sdk_helpers
from r7_surcom_sdk.lib.sdk_terminal_fonts import colors, fmt

LOG = logging.getLogger(constants.LOGGER_NAME)

# TODO: add mockserver tests for this file


class SurcomAPI():

    def __init__(
        self,
        base_url: str,
        api_key: str,
        user_agent_str: str = None
    ):
        """
        The main class for the Surface Command API

        :param base_url: the base URL of the Surface Command API
        :type base_url: str
        :param api_key: the API key to use for authentication. If using the legacy format, this should be in the format:
            '__legacy__<tenant_id>/<username>:<password>'
        :type api_key: str, optional
        :param user_agent_str: an optional user agent string to append to the default user agent
            (r7-surcom-sdk/<version>). This is useful for debugging and logging purposes.
            This should be a string that describes the client using the SDK, e.g. 'import-data command'
        :type user_agent_str: str, optional
        """

        # TODO: validate the url
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.session()

        user_agent = f"{constants.FULL_PROGRAM_NAME}/{version(constants.PACKAGE_NAME)}"

        if user_agent_str:
            user_agent = f"{user_agent}/{user_agent_str}"

        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip"
        })

        if api_key.startswith(constants.LEGACY_PREFIX):

            if ":" not in api_key or "/" not in api_key:
                raise SurcomSDKException(
                    "If using the legacy format to authenticate, make sure the api_key is in the format: "
                    "'__legacy__<tenant_id>/<username>:<password>'"
                )

            username, pw = api_key.replace(constants.LEGACY_PREFIX, "").split(":")
            self.session.auth = HTTPBasicAuth(username=username, password=pw)
            self.using_api_key = False

        else:
            self.session.headers.update({"X-API-Key": api_key})
            self.using_api_key = True

    def _request(
            self,
            method: str,
            url: str,
            params: dict = None,
            data: dict = None,
            json: dict = None,
            headers: dict = None,
            timeout: float = constants.REQUESTS_TIMEOUT_SECONDS,
            return_response_object: bool = False
    ) -> dict:
        """
        The main method that sends all requests to Surface Command

        :param method: the request method. One of GET, POST, PUT or DELETE
        :type method: str
        :param url: the URL of the API in Surface Command to send the request to
        :type url: str
        :param params: dict of parameters to send in the query string for the Request
        :type params: dict, optional
        :param data: dict, bytes, or file-like object to send in the body of the Request
        :type data: dict, optional
        :param json: a JSON serializable Python object to send in the body of the Request
        :type json: dict, optional
        :param headers: dictionary of extra HTTP Headers to send with the Request. Headers set in the
            __init__ method are sent with every request
        :type headers: dict, optional
        :param timeout: How many seconds to wait for the server to send data before giving up,
            defaults to constants.REQUESTS_TIMEOUT_SECONDS
        :type timeout: float, optional
        :param return_response_object: if set to True returns the requests.response object, defaults to False
        :type return_response_object: bool, optional
        :return: The body of the response as a dict or the full requests.Response object if `return_response_object`
            is set to True
        :rtype: dict
        """
        # TODO: what about cert files
        rtn_value = None

        if method not in constants.REQUEST_SUPPORTED_METHODS:
            raise SurcomSDKException(f"'{method}' is not one of '{','.join(constants.REQUEST_SUPPORTED_METHODS)}'")

        r = self.session.request(
            method=method,
            url=f"{self.base_url}/{url}",
            params=params,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout
        )

        try:
            trace_id = r.headers.get(constants.HEADER_NOETIC_TRACE_ID)

            if trace_id:
                LOG.debug(f"{fmt(constants.HEADER_NOETIC_TRACE_ID, c=colors.RED)}: {trace_id}")

            r.raise_for_status()

            if return_response_object:
                return r

        except HTTPError as err:

            LOG.debug(f"Error Response: {str(err)}")

            err_detail = r.text

            try:
                err_detail = r.json()

                # Sometimes an error message is a just a plain str
                # (yeah, even after we call .json())
                if isinstance(err_detail, str):
                    raise SurcomSDKException(err_detail)

                # Sometimes errors are in "message"
                err_detail = err_detail.get("message", err_detail)

                # Sometimes errors are then nested in "detail"
                if isinstance(err_detail, dict):
                    err_detail.get("detail", err_detail)

            except requests.exceptions.JSONDecodeError:
                LOG.debug("We could not decode the JSON error message")

            if self.using_api_key and r.status_code == 403:
                err_msg = f"This API Key does not have the correct permissions.\nERROR: {err_detail}\n{str(err)}"
                raise SurcomSDKException(err_msg)

            if err_detail:
                sdk_helpers.print_log_msg(err_detail, log_level=logging.ERROR)

                # No need to show the Python traceback if we get a valid
                # error message from the server
                sys.tracebacklimit = 0

            if trace_id:
                sdk_helpers.print_log_msg(f"X-Noetic-Trace-Id: {trace_id}", log_level=logging.ERROR)

            raise err

        try:
            rtn_value = r.json()
        except requests.exceptions.JSONDecodeError:
            LOG.debug(f"We failed to get json from the response: {str(r)}")
            rtn_value = r.text

        return rtn_value

    def import_batch_create(
        self,
        import_id: str,
        execution_id: str = None
    ) -> str:
        """
        Create a batch for an import in Surface Command

        :param import_id: the id of the import
        :type import_id: str
        :param execution_id: an optional execution_id to give the workflow that
            invokes the batch, defaults to None
        :type execution_id: str, optional
        :return: the id of the created batch
        :rtype: str
        """
        params = None

        if execution_id:
            params = {"execution_id": execution_id}

        r = self._request(
            method="POST",
            url=f"graph-api/batch/{import_id}",
            params=params
        )

        batch_id = r.get("items", [])[0].get("content", {}).get("id")

        return batch_id

    def import_batch_add_data(
        self,
        import_id: str,
        batch_id: str,
        data: dict
    ) -> str:

        params = {
            "import_id": import_id,
            "batch_id": batch_id
        }

        r = self._request(
            method="POST",
            url="graph-api/objects",
            params=params,
            json=data
        )

        return r

    def import_batch_finalize(
        self,
        import_id: str,
        batch_id: str
    ):
        """
        Finalize an import batch in Surface Command

        :param import_id: the id of the import
        :type import_id: str
        :param batch_id: the id of the batch to finalize
        :type batch_id: str
        """
        r = self._request(
            method="POST",
            url=f"graph-api/batch/{import_id}/{batch_id}"
        )

        return r

    def types_get(
        self,
        type_name: str,
        params: dict = None
    ) -> dict:
        """
        Get a type in Surface Command

        :param type_name: the name of the type to get (this is the type_id)
        :type type_name: str
        """

        try:
            r = self._request(
                method="GET",
                url=f"schema-api/types/{type_name}",
                params=params
            )
        except SurcomSDKException as err:
            if "not found" in str(err):
                return None

            raise err

        return r

    def types_create(
        self,
        content: dict
    ):
        """
        Create a type in Surface Command

        :param content: the content of the type to create
        :type content: dict
        """
        type_name = content.get(constants.X_SAMOS_TYPE_NAME)
        type_to_upload = {type_name: content}

        if not type_name:
            raise SurcomSDKException(
                f"Type name is required. Nothing found for key '{constants.X_SAMOS_TYPE_NAME}'",
            )

        r = self._request(
            method="POST",
            url="schema-api/types",
            json=type_to_upload
        )

        return r

    def app_status(
        self,
        connector_id: str
    ) -> dict:
        """
        Get the status of an app (Connector) in Surface Command

        :param connector_id: the id of the app to get the status of
        :type connector_id: str
        :return: the status of the app
        :rtype: dict
        """

        if not connector_id:
            raise SurcomSDKException(
                "'connector_id' is required to get the status of an Connector"
            )

        r = self._request(
            method="GET",
            url="apps-api/apps/info/status",
            params={"integration_ids": connector_id}
        )

        err_msg = f"Failed to get the status for Connector '{connector_id}'. Response: {str(r)}"

        if not isinstance(r, list):
            LOG.debug("The response is not a list, we cannot get the status")
            raise SurcomSDKException(err_msg)

        if len(r) >= 1:

            statuses = r[0].get("statuses", [])

            if statuses and isinstance(statuses, list) and len(statuses) == 1:
                return statuses[0]

        raise SurcomSDKException(err_msg)
