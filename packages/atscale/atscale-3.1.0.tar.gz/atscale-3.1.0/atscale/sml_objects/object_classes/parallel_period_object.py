from typing import List

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class ParallelPeriodObject(SemanticObject):
    _required_keys = [
        "level",
        "key_columns",
    ]
    _optional_keys = []

    def __init__(
        self,
        level: str,
        key_columns: List[str],
    ):
        """An object that defines a custom parallel period for a level.

        Args:
            level (str): The name of the level for which the parallel period is defined.
            key_columns (List[str]): The key columns for the parallel period.
        """
        self._object_type = SemanticObjectTypes.PARALLEL_PERIOD

        self._level = level
        self._key_columns = key_columns

        object_dict = {
            "level": self._level,
            "key_columns": self._key_columns,
        }

        self._object_dict = object_dict
        self._file_path = None

    @property
    def level(self) -> str:
        """Getter for the level instance variable

        Returns:
            str: The level for the parallel period
        """
        return self._level

    @level.setter
    def level(
        self,
        value,
    ):
        """Setter for the level instance variable. This variable is final, you must construct a new ParallelPeriodObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def key_columns(self) -> List[str]:
        """Getter for the key_columns instance variable

        Returns:
            List[str]: The key columns for the parallel period
        """
        return self._key_columns

    @key_columns.setter
    def key_columns(
        self,
        value,
    ):
        """Setter for the key_columns instance variable. This variable is final, you must construct a new ParallelPeriodObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_columns is final; it cannot be altered."
        )
