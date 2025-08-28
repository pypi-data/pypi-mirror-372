from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.base.private_enums import SemanticObjectTypes


class MetricObject(YamlObject):
    _required_keys = [
        "unique_name",
        "label",
        "calculation_method",
        "dataset",
        "column",
    ]
    _optional_keys = [
        "description",
        "format",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        calculation_method: str,
        dataset: str,
        column: str,
        label: str = None,
        description: str = None,
        format: str = None,
        is_hidden: bool = False,
    ):
        """Represents an aggregation method over a numeric column

        Args:
            unique_name (str): the name of the metric, how it will appear in queries
            calculation_method (str): the aggregation method
            dataset (str): the dataset this metric is built off of
            column (str): the column within the dataset that this metric is built off of
            label (str, optional): the name of the metric in BI tools. Defaults to None to use the unique_name
            description (str, optional): the description of this metric. Defaults to None to leave blank
            format (str, optional): the custom formatting of the metric's output. Defaults to None to leave blank
            is_hidden (bool, optional): if the metric should be hidden from BI tools. Defaults to False
        """
        self._object_type = SemanticObjectTypes.METRIC
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._calculation_method = calculation_method
        self._dataset = dataset
        self._column = column
        self._description = description
        self._format = format
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "object_type": self._object_type.value,
            "label": self._label,
            "calculation_method": self._calculation_method,
            "dataset": self._dataset,
            "column": self._column,
        }
        if description is not None:
            object_dict["description"] = self._description
        if format is not None:
            object_dict["format"] = self._format
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden

        self._object_dict = object_dict
        self._file_path = None

    @property
    def calculation_method(self) -> str:
        """Getter for the calculation_method instance variable

        Returns:
            str: The calculation_method of this metric
        """
        return self._calculation_method

    @calculation_method.setter
    def calculation_method(
        self,
        value,
    ):
        """Setter for the calculation_method instance variable. This variable is final, you must construct a new MetricObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of calculation_method is final; it cannot be altered."
        )

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this metric
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new MetricObject.

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
            str: The column of this metric
        """
        return self._column

    @column.setter
    def column(
        self,
        value,
    ):
        """Setter for the column instance variable. This variable is final, you must construct a new MetricObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of column is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this metric
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
    def format(self) -> str:
        """Getter for the format instance variable

        Returns:
            str: The format of this metric
        """
        return self._format

    @format.setter
    def format(
        self,
        value,
    ):
        """Setter for the format instance variable. This variable is final, you must construct a new Metric.

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
            bool: The is_hidden of this metric
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable.This variable is final, you must construct a new Metric.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )
