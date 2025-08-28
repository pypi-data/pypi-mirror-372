from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class IncrementalObject(SemanticObject):
    _required_keys = [
        "column",
        "grace_period",
    ]
    _optional_keys = []

    def __init__(
        self,
        column: str,
        grace_period: str,
    ):
        """Represents a dataset's incremental build options

        Args:
            column (str): the column to apply the grace_period for
            grace_period (str): the grace_period for the given column
        """

        self._object_type = SemanticObjectTypes.INCREMENTAL
        self._column = column
        self._grace_period = grace_period

        self._object_dict = {
            "grace_period": self._grace_period,
            "column": self._column,
        }

    @property
    def column(self) -> str:
        """Getter for the column instance variable

        Returns:
            str: The column of this incremental
        """
        return self._column

    @column.setter
    def column(
        self,
        value,
    ):
        """Setter for the column instance variable. This variable is final, you must construct a new IncrementalObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of column is final; it cannot be altered."
        )

    @property
    def grace_period(self) -> str:
        """Getter for the grace_period instance variable

        Returns:
            str: The grace_period of this incremental
        """
        return self._grace_period

    @grace_period.setter
    def grace_period(
        self,
        value,
    ):
        """Setter for the grace_period instance variable. This variable is final, you must construct a new IncrementalObject.

        Args:
            value: setter grace_period be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of grace_period is final; it cannot be altered."
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
