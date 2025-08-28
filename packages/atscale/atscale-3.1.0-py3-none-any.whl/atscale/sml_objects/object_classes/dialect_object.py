from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class DialectObject(SemanticObject):
    _required_keys = [
        "dialect",
        "sql",
    ]
    _optional_keys = []

    def __init__(
        self,
        dialect: str,
        sql: str,
    ):
        """Represents a alternatice sql for an object

        Args:
            dialect (str): the dialect to apply the sql for
            sql (str): the sql for the given dialect
        """

        self._object_type = SemanticObjectTypes.DIALECT
        self._dialect = dialect
        self._sql = sql

        self._object_dict = {
            "sql": self._sql,
            "dialect": self._dialect,
        }

    @property
    def dialect(self) -> str:
        """Getter for the dialect instance variable

        Returns:
            str: The dialect of this dialect
        """
        return self._dialect

    @dialect.setter
    def dialect(
        self,
        value,
    ):
        """Setter for the dialect instance variable. This variable is final, you must construct a new DialectObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dialect is final; it cannot be altered."
        )

    @property
    def sql(self) -> str:
        """Getter for the sql instance variable

        Returns:
            str: The sql of this dialect
        """
        return self._sql

    @sql.setter
    def sql(
        self,
        value,
    ):
        """Setter for the sql instance variable. This variable is final, you must construct a new DialectObject.

        Args:
            value: setter sql be used.
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
