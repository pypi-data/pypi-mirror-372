"""
Module a class that represents a Connector
"""

from r7_surcom_sdk.lib import SurcomSDKException, constants

# A common place that stores Connectors that have
# been read from disk before
ALL_CONNECTORS: 'set[Connector]' = set()


class Connector(object):
    def __init__(
        self,
        conn_spec_data: dict = {},
        manifest_data: dict = {},
        path_src_code: str = None
    ):

        if not conn_spec_data and not manifest_data:
            raise SurcomSDKException(
                f"Connector must be initialized with either "
                f"a {constants.CONN_SPEC_YAML} or {constants.MANIFEST_YAML} file"
            )

        if conn_spec_data:

            self.id: str = conn_spec_data.get("id", None)
            self.name: str = conn_spec_data.get("name", None)
            self.version: str = conn_spec_data.get("version", None)
            self.type = constants.SURCOM_CONNECTOR

        elif manifest_data:

            self.id: str = manifest_data.get("id", None)
            self.name: str = manifest_data.get("name", None)
            self.version: str = manifest_data.get("version", None)
            self.type = constants.LEGACY_CONNECTOR

        self.conn_spec: dict = conn_spec_data
        self.manifest: dict = manifest_data
        self.path_src_code: str = path_src_code

    def __eq__(self, value: object) -> bool:
        return self.id == value.id

    def __repr__(self) -> str:
        return f"{self.name}_v{self.version}"

    def __str__(self) -> str:
        return self.__repr__()

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self) -> int:
        return hash(self.id)
