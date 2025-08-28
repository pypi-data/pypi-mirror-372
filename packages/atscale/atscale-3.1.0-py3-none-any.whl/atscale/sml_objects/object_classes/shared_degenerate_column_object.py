from typing import List
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class SharedDegenerateColumnObject(SemanticObject):

    _required_keys = [
        "dataset",
        "name_column",
        "key_columns",
    ]

    _optional_keys = [
        "sort_column",
        "is_unique_key",
    ]

    def __init__(
        self,
        dataset: str,
        name_column: str,
        key_columns: List[str],
        sort_column: str = None,
        is_unique_key: bool = None,
    ):
        """Represents a shared degenerate column.

        Args:
            dataset (str): The fact dataset that the shared degenerate column is based on.
            name_column (str): The column from the dataset whose values appear for the dimension
            in the consumption tool.
            key_columns (List[str]): The column from the dataset that the shared degenerate
            dimension is based on.
            sort_column (str, optional): The column from the dataset that is used to sort query
            results. Defaults to None.
            is_unique_key (bool, optional): Determines whether values of the key_columns column
            are unique for each row. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.SHARED_DEGENERATE_COLUMN
        self._dataset = dataset
        self._name_column = name_column
        self._key_columns = key_columns
        self._sort_column = sort_column
        self._is_unique_key = is_unique_key

        object_dict = {
            "dataset": self._dataset,
            "name_column": self._name_column,
            "key_columns": self._key_columns,
        }

        if sort_column is not None:
            object_dict["sort_column"] = self._sort_column
        if is_unique_key is not None:
            object_dict["is_unique_key"] = self._is_unique_key

        self._object_dict = object_dict

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this shared degenerate column
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new SharedDegenerateColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset is final; it cannot be altered."
        )

    @property
    def name_column(self) -> str:
        """Getter for the name column instance variable

        Returns:
            str: The name_column of this shared degenerate column
        """
        return self._name_column

    @name_column.setter
    def name_column(
        self,
        value,
    ):
        """Setter for the name column instance variable. This variable is final, you must construct a new SharedDegenerateColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name_column is final; it cannot be altered."
        )

    @property
    def key_columns(self) -> str:
        """Getter for the key columns instance variable

        Returns:
            str: The key_columns of this shared degenerate column
        """
        return self._key_columns

    @key_columns.setter
    def key_columns(
        self,
        value,
    ):
        """Setter for the key columns instance variable. This variable is final, you must construct a new SharedDegenerateColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_columns is final; it cannot be altered."
        )

    @property
    def sort_column(self) -> str:
        """Getter for the sort column instance variable

        Returns:
            str: The sort_column of this shared degenerate column
        """
        return self._sort_column

    @sort_column.setter
    def sort_column(
        self,
        value,
    ):
        """Setter for the sort column instance variable. This variable is final, you must construct a new SharedDegenerateColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sort_column is final; it cannot be altered."
        )

    @property
    def is_unique_key(self) -> str:
        """Getter for the is_unique_key instance variable

        Returns:
            str: The is_unique_key of this shared degenerate column
        """
        return self._is_unique_key

    @is_unique_key.setter
    def is_unique_key(
        self,
        value,
    ):
        """Setter for the is_unique_key instance variable. This variable is final, you must construct a new SharedDegenerateColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_unique_key is final; it cannot be altered."
        )
