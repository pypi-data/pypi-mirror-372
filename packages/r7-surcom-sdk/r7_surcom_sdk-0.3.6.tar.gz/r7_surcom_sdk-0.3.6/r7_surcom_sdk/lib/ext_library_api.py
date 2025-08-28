
import logging

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from r7_surcom_sdk.lib import constants, sdk_config, SurcomSDKException

LOG = logging.getLogger(constants.LOGGER_NAME)


class ExtLibraryAPI:
    """
    This class provides an interface to the Extensions Library API
    """

    def __init__(self):

        # Try get a custom URL from the surcom_config file, else use the default URL
        ext_lib_url = sdk_config.get_config(
            constants.CONFIG_NAME_EXT_LIB_URL,
            default=constants.DEFAULT_EXT_LIB_API_URL
        )

        self.base_url = ext_lib_url
        self.session = requests.session()

    def _get(
        self,
        endpoint: str,
        params: dict = None,
        timeout: float = constants.REQUESTS_TIMEOUT_SECONDS,
    ):
        r = self.session.get(
            url=f"{self.base_url}/{endpoint}",
            params=params,
            timeout=timeout
        )

        r.raise_for_status()

        return r

    def is_enabled(self) -> bool:
        """
        If the `use_extensions_library` setting is set to False,
        then the Extensions Library API is not enabled.

        If the setting is not found or set to True,
        then the Extensions Library API is enabled.

        :return: False if the `use_extensions_library` setting in the surcom_config file is set to False,
            True otherwise
        :rtype: bool
        """

        return sdk_config.get_config(
            option=constants.CONFIG_NAME_USE_EXT_LIB,
            option_type="bool",
            default=True
        )

    def get_extension(
        self,
        connector_id: str
    ) -> dict:
        """
        Get an Extension (Connector) from the Extensions Library by its ID

        :param connector_id: the ID of the Connector to retrieve
        :type connector_id: str
        :return: the Extension (Connector) data as a JSON object
        :rtype: dict
        """

        if not connector_id:
            raise SurcomSDKException("Connector ID cannot be empty")

        # NOTE: the extension_id is the connector_id with '.' replaced by '_'
        # and 'app' appended to it
        extension_id = f"{connector_id.lower().replace('.', '_')}_app"

        endpoint = f"v2/public/extensions/{extension_id}"
        r = self._get(endpoint=endpoint, timeout=3)

        try:
            rtn_value = r.json()
        except JSONDecodeError:
            LOG.debug(f"We failed to get json from the response: {str(r)}")
            return None

        return rtn_value

    def get_connector_version_history(
        self,
        connector_id: str
    ) -> list:
        """
        Get the version history of a Connector by its ID

        :param connector_id: the ID of the Connector to retrieve the version history for
        :type connector_id: str
        :return: a list of versions for the Connector
        :rtype: list
        """

        try:
            extension = self.get_extension(connector_id=connector_id)
        except HTTPError as err:
            LOG.debug(f"We could not find the Connector '{connector_id}' on the Extension Library: {str(err)}")
            return []

        if not extension:
            LOG.debug(f"No extension found for connector ID '{connector_id}'")
            return []

        return extension.get("versionHistory", [])
