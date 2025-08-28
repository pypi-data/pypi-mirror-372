from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class MetricalAttributeObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
        "dataset",
        "column",
        "calculation_method",
    ]
    _optional_keys = [
        "description",
        "folder",
        "format",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        dataset: str,
        column: str,
        calculation_method: str,
        label: str = None,
        description: str = None,
        folder: str = None,
        format: str = None,
        is_hidden: bool = None,
    ):
        """The object describing metrical attribute attributes.

        Args:
            unique_name (str): the name of the metrical attribute, how it will appear in queries
            dataset (str): The source dataset containing the column that the metrical attribute is based on
            column (str): The dataset column that the metrical attribute is based on.
            calculation_method (str): The calculation to apply to the data.
            label (str, optional): the name of the metrical attribute in BI tools. Defaults to None to use the unique_name
            description (str, optional): The description of the metrical attribute. Defaults to None.
            folder (str, optional): The folder to which the metrical attribute belongs. Defaults to None.
            format (str, optional): The format in which query results are returned. Defaults to None.
            is_hidden (bool, optional): Whether the metrical attribute is visible in consumption tools. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.METRICAL_ATTRIBUTE
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._dataset = dataset
        self._column = column
        self._calculation_method = calculation_method
        self._description = description
        self._folder = folder
        self._format = format
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "label": self.label,
            "dataset": self._dataset,
            "column": self._column,
            "calculation_method": self._calculation_method,
        }
        if description is not None:
            object_dict["description"] = self._description
        if folder is not None:
            object_dict["folder"] = self._folder
        if format is not None:
            object_dict["format"] = self._format
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden

        self._object_dict = object_dict

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this metrical attribute
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. This variable is final, you must construct a new MetricalAttributeObject.

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
            str: The dataset of this metrical attribute
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new MetricalAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset is final; it cannot be altered."
        )

    @property
    def column(self) -> str:
        """Getter for the column instance variable

        Returns:
            str: The dataset column that this metrical attribute is based on
        """
        return self._column

    @column.setter
    def column(
        self,
        value,
    ):
        """Setter for the column instance variable. This variable is final, you must construct a new MetricalAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of column is final; it cannot be altered."
        )

    @property
    def calculation_method(self) -> str:
        """Getter for the calculation_method instance variable

        Returns:
            str: The calculation method to apply to the data
        """
        return self._calculation_method

    @calculation_method.setter
    def calculation_method(
        self,
        value,
    ):
        """Setter for the calculation_method instance variable. This variable is final, you must construct a new MetricalAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of calculation_method is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of the metrical attribute
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
            str: The folder of the metrical attribute
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new MetricalAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )

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
        """Setter for the format instance variable. This variable is final, you must construct a new MetricalAttributeObject.

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
            bool: Whether the metrical attribute is visible in consumption tools
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new MetricalAttributeObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )
