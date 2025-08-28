from typing import Dict
from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.base.private_enums import SemanticObjectTypes


class ConnectionObject(YamlObject):
    _required_keys = [
        "unique_name",
        "as_connection",
        "database",
        "schema",
        "label",
    ]
    _optional_keys = []

    def __init__(
        self,
        unique_name: str,
        as_connection: str,
        database: str,
        schema: str,
        label: str = None,
    ):
        """Represents a connection to a database and schema

        Args:
            unique_name (str): The name of the connection.
            as_connection (str): The AtScale connection to associate with this connection.
            database (str): The database for this connection.
            schema (str): The schema for this connection.
            label (str, optional): The user facing name of the connection. Defaults to None to use the unique_name.
        """
        self._object_type = SemanticObjectTypes.CONNECTION
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._as_connection = as_connection
        self._database = database
        self._schema = schema

        self._object_dict = {
            "unique_name": self._unique_name,
            "object_type": self._object_type.value,
            "label": self._label,
            "as_connection": self._as_connection,
            "database": self._database,
            "schema": self._schema,
        }

        self._file_path = None

    @property
    def as_connection(self) -> str:
        """Getter for the as_connection instance variable

        Returns:
            str: The as_connection of this connection
        """
        return self._as_connection

    @as_connection.setter
    def as_connection(
        self,
        value,
    ):
        """Setter for the as_connection instance variable. This variable is final, you must construct a new ConnectionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of as_connection is final; it cannot be altered."
        )

    @property
    def database(self) -> str:
        """Getter for the database instance variable

        Returns:
            str: The database of this connection
        """
        return self._database

    @database.setter
    def database(
        self,
        value,
    ):
        """Setter for the database instance variable. This variable is final, you must construct a new ConnectionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of database is final; it cannot be altered."
        )

    @property
    def schema(self) -> str:
        """Getter for the schema instance variable

        Returns:
            str: The schema of this connection
        """
        return self._schema

    @schema.setter
    def schema(
        self,
        value,
    ):
        """Setter for the schema instance variable. This variable is final, you must construct a new ConnectionObject.

        Args:
            value: setter schema be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of schema is final; it cannot be altered."
        )
