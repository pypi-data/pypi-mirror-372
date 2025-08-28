from typing import List

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class SecondaryAttributeObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
        "dataset",
        "name_column",
        "key_columns",
    ]
    _optional_keys = [
        "description",
        "folder",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        dataset: str,
        name_column: str,
        key_columns: List[str],
        label: str = None,
        description: str = None,
        folder: str = None,
        is_hidden: bool = None,
    ):
        """Dimensional attribute which is not the dimension's key and not part of a hierarchy.

        Args:
            unique_name (str): the name of the secondary attribute, how it will appear in queries
            dataset (str): The name of the dataset that contains the `key_columns` which the secondary attribute is based on.
            name_column (str): The dataset column that the secondary attribute is based on.
            key_columns (List[str]): The key columns that the secondary attribute is based on.
            label (str, optional): The name of the secondary attribute as it appears in the consumption tool. Defaults to None to use unique_name
            description (str, optional): The description of the secondary attribute. Defaults to None.
            folder (str, optional): The folder to which the secondary attribute belongs. Defaults to None.
            is_hidden (bool, optional): Whether the secondary attribute is visible in consumption tools. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.SECONDARY_ATTRIBUTE
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._dataset = dataset
        self._name_column = name_column
        self._key_columns = key_columns
        self._description = description
        self._folder = folder
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
            "dataset": self._dataset,
            "name_column": self._name_column,
            "key_columns": self._key_columns,
        }
        if description is not None:
            object_dict["description"] = self._description
        if folder is not None:
            object_dict["folder"] = self._folder
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden

        self._object_dict = object_dict

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this secondary attribute
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of label is final; it cannot be altered."
        )

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this secondary attribute
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset is final; it cannot be altered."
        )

    @property
    def name_column(self) -> str:
        """Getter for the name_column instance variable

        Returns:
            str: The dataset column that this secondary attribute is based on
        """
        return self._name_column

    @name_column.setter
    def name_column(
        self,
        value,
    ):
        """Setter for the name_column instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name_column is final; it cannot be altered."
        )

    @property
    def key_columns(self) -> str:
        """Getter for the key_columns instance variable

        Returns:
            str: The key columns that this secondary attribute is based on
        """
        return self._key_columns

    @key_columns.setter
    def key_columns(
        self,
        value,
    ):
        """Setter for the key_columns instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_columns is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of the secondary attribute
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable.

        Args:
            value: The value to which description will be set.
        """
        self._description = value
        self._object_dict["description"] = value

    @property
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder of the secondary attribute
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )

    @property
    def is_hidden(self) -> bool:
        """Getter for the is_hidden instance variable

        Returns:
            bool: Whether the secondary attribute is visible in consumption tools
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new SecondaryAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )
