from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class CalculatedMemberObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "expression",
    ]
    _optional_keys = [
        "description",
        "format",
    ]

    def __init__(
        self,
        unique_name: str,
        expression: str,
        description: str = None,
        format: str = None,
    ):
        """A class representing the calculated members to incorporate in a given calculated group.

        Args:
            unique_name (str): The name of this calculated member
            expression (str): The MDX expression for this calculated member
            description (str, optional): The description of this calculated member. Defaults to None.
            format (str, optional): The format in which query results are returned. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.CALCULATED_MEMBER
        self._unique_name = unique_name

        self._expression = expression
        self._description = description
        self._format = format

        object_dict = {
            "unique_name": self._unique_name,
            "expression": self._expression,
        }
        if description is not None:
            object_dict["description"] = self._description
        if format is not None:
            object_dict["format"] = self._format

        self._object_dict = object_dict

    @property
    def expression(self) -> str:
        """Getter for the expression instance variable

        Returns:
            str: The MDX expression for this calculated member
        """
        return self._expression

    @expression.setter
    def expression(
        self,
        value,
    ):
        """Setter for the expression instance variable. This variable is final, you must construct a new CalculatedMemberObject.

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
            str: The description of this calculated member
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable

        Args:
            value: The value to which description will be set
        """
        self._description = value
        self._object_dict["description"] = value

    @property
    def format(self) -> str:
        """Getter for the format instance variable

        Returns:
            str: The format in which query results are returned
        """
        return self._format

    @format.setter
    def format(
        self,
        value,
    ):
        """Setter for the format instance variable. This variable is final, you must construct a new CalculatedMemberObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of format is final; it cannot be altered."
        )
