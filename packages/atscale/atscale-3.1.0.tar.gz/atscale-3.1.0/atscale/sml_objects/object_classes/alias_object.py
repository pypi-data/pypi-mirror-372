from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class AliasObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
        "dataset",
        "name_column",
    ]
    _optional_keys = [
        "sort_column",
        "description",
        "folder",
        "format",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        dataset: str,
        name_column: str,
        sort_column: str,
        label: str = None,
        description: str = None,
        folder: str = None,
        format: str = None,
        is_hidden: bool = None,
    ):
        """Aliases for specific hierarchy levels within consumption tools.

        Args:
            unique_name (str): the name of the alias, how it will appear in queries
            dataset (str): The source dataset containing the column that the alias is based on
            name_column (str): The dataset column that the alias is based on.
            sort_column (str): The column to use to sort values in result sets.
            label (str, optional): The name of the alias as it appears in the consumption tool. Defaults to None to use unique_name
            description (str, optional): The description of the alias. Defaults to None.
            folder (str, optional): The folder to which the alias belongs. Defaults to None.
            format (str, optional): The format in which query results are returned. Defaults to None.
            is_hidden (bool, optional): Whether the alias is visible in consumption tools. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.ALIAS
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._dataset = dataset
        self._name_column = name_column
        self._sort_column = sort_column
        self._description = description
        self._folder = folder
        self._format = format
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
            "dataset": self._dataset,
            "name_column": self._name_column,
        }
        if sort_column is not None:
            object_dict["sort_column"] = self._sort_column
        if description is not None:
            object_dict["description"] = self._description
        if folder is not None:
            object_dict["folder"] = self._folder
        if format is not None:
            object_dict["format"] = self._format
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden

        self._object_dict = object_dict
        self._file_path = None

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this alias
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. This variable is final, you must construct a new AliasObject.

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
            str: The dataset of this alias
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new AliasObject.

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
            str: The dataset column that this alias is based on
        """
        return self._name_column

    @name_column.setter
    def name_column(
        self,
        value,
    ):
        """Setter for the name_column instance variable. This variable is final, you must construct a new AliasObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name_column is final; it cannot be altered."
        )

    @property
    def sort_column(self) -> str:
        """Getter for the sort_column instance variable

        Returns:
            str: The column to use to sort the values in result sets.
        """
        return self._sort_column

    @sort_column.setter
    def sort_column(
        self,
        value,
    ):
        """Setter for the sort_column instance variable. This variable is final, you must construct a new AliasObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sort_column is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of the alias
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
            str: The folder of the alias
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable.

        Args:
            value: The value to which folder will be set.
        """
        self._folder = value
        self._object_dict["folder"] = value

    @property
    def format(self) -> str:
        """Getter for the format instance variable

        Returns:
            str: The format in which the query results are returned
        """
        return self._format

    @format.setter
    def format(
        self,
        value,
    ):
        """Setter for the format instance variable. This variable is final, you must construct a new AliasObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of format is final; it cannot be altered."
        )

    @property
    def is_hidden(self) -> bool:
        """Getter for the is_hidden instance variable

        Returns:
            bool: Whether the alias is visible in consumption tools
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new AliasObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )
