from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.base.private_enums import SemanticObjectTypes


class CalculationObject(YamlObject):

    _required_keys = ["unique_name", "expression", "label"]
    _optional_keys = [
        "description",
        "format",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        expression: str,
        label: str = None,
        description: str = None,
        format: str = None,
        is_hidden: bool = False,
    ):
        """Represents a custom MDX expression for creating calculated metrics in AtScale.

        Args:
            unique_name (str): the name of the calculation, how it will appear in queries
            expression (str): the MDX expression to use for the calculation
            label (str, optional): the name of the calculation in BI tools. Defaults to None to use the unique_name
            description (str, optional): the description of this calculation. Defaults to None to leave blank
            format (str, optional): the custom formatting of the calculation's output. Defaults to None to leave blank
            is_hidden (bool, optional): if the calculation should be hidden from BI tools. Defaults to False
        """
        self._object_type = SemanticObjectTypes.CALCULATION
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._expression = expression
        self._description = description
        self._format = format
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "object_type": self._object_type.value,
            "label": self._label,
            "expression": self._expression,
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
    def expression(self) -> str:
        """Getter for the expression instance variable

        Returns:
            str: the MDX expression to use for the calculation
        """
        return self._expression

    @expression.setter
    def expression(
        self,
        value,
    ):
        """Setter for the expression instance variable. This variable is final, you must construct a new CalculationObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of expression is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this calculation
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
            str: The format of this calculation
        """
        return self._format

    @format.setter
    def format(
        self,
        value,
    ):
        """Setter for the format instance variable. This variable is final, you must construct a new Calculation.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of format is final; it cannot be altered."
        )

    @property
    def is_hidden(self) -> str:
        """Getter for the is_hidden instance variable

        Returns:
            str: The is_hidden of this calculation
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new Calculation.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )
