from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class PerspectiveHierarchyObject(SemanticObject):
    _required_keys = ["name"]
    _optional_keys = ["levels"]

    def __init__(
        self,
        name: str,
        levels: list[str] = None,
    ):
        """Represents a perspective hierarchy

        Args:
            name (str): The name of the hierarchy.
            levels (list[str], optional): The levels of the hierarchy. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.PERSPECTIVE_HIERARCHY
        self._name = name
        self._levels = levels

        self._object_dict = {"name": self._name}
        if levels is not None:
            self._object_dict["levels"] = levels

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The name of this hierarchy
        """
        return self._name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, you must construct a new PerspectiveHierarchyObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def levels(self) -> list[str]:
        """Getter for the levels instance variable

        Returns:
            str: The levels of this hierarchy
        """
        return self._levels

    @levels.setter
    def levels(
        self,
        value,
    ):
        """Setter for the levels instance variable. This variable is final, you must construct a new PerspectiveHierarchyObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of levels is final; it cannot be altered."
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
