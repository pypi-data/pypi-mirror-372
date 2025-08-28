from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class AlternateObject(SemanticObject):
    _required_keys = ["type"]
    _optional_keys = ["table", "connection_id", "sql"]

    def __init__(
        self,
        type: str,
        connection_id: str = None,
        table: str = None,
        sql: str = None,
    ):
        """Represents an alternate database location

        Args:
            type (str): The type of alternate.
            connection_id (str, optional): The connection to use.
            table (str, optional): The table name. Defaults to None.
            sql (str, optional): The sql query if defining a QDS. Defaults to None.
        """
        if sql is None and (table is None or connection_id is None):
            raise atscale_errors.ValidationError(
                "sql or table and connection_id must be provided; table and connection_id must be provided together."
            )

        if sql is not None and (table is not None or connection_id is not None):
            raise atscale_errors.ValidationError(
                "Either sql or table and connection_id must be provided, not both."
            )

        self._object_type = SemanticObjectTypes.ALTERNATE
        self._type = type
        self._connection_id = connection_id
        self._table = table
        self._sql = sql

        self._object_dict = {"type": self._type}
        if self._sql is not None:
            self._object_dict["sql"] = self._sql
        if self._connection_id is not None:
            self._object_dict["connection_id"] = self._connection_id
        if self._table is not None:
            self._object_dict["table"] = self._table

    @property
    def type(self) -> str:
        """Getter for the type instance variable

        Returns:
            str: The type of this alternate
        """
        return self._type

    @type.setter
    def type(
        self,
        value,
    ):
        """Setter for the type instance variable. This variable is final, you must construct a new AlternateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of type is final; it cannot be altered."
        )

    @property
    def connection_id(self) -> str:
        """Getter for the connection_id instance variable

        Returns:
            str: The connection_id of this alternate
        """
        return self._connection_id

    @connection_id.setter
    def connection_id(
        self,
        value,
    ):
        """Setter for the connection_id instance variable. This variable is final, you must construct a new AlternateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of connection_id is final; it cannot be altered."
        )

    @property
    def table(self) -> str:
        """Getter for the table instance variable

        Returns:
            str: The table of this alternate
        """
        return self._table

    @table.setter
    def table(
        self,
        value,
    ):
        """Setter for the table instance variable. This variable is final, you must construct a new AlternateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of table is final; it cannot be altered."
        )

    @property
    def sql(self) -> str:
        """Getter for the sql instance variable

        Returns:
            str: The sql of this alternate
        """
        return self._sql

    @sql.setter
    def sql(
        self,
        value,
    ):
        """Setter for the sql instance variable. This variable is final, you must construct a new AlternateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sql is final; it cannot be altered."
        )

    @property
    def unique_name(self) -> str:
        """Getter for the unique_name instance variable. Not implemented for this object

        Returns:
            str: Nothing
        """
        raise NotImplementedError

    @unique_name.setter
    def unique_name(
        self,
        value,
    ):
        """Setter for the unique_name instance variable. Not implemented for this object.

        Args:
            value: Nothing
        """
        raise NotImplementedError
