from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes
from atscale.base.private_enums import SemanticObjectTypes, PartitionTypes


class PartitionObject(SemanticObject):
    _required_keys = ["unique_name", "dimension", "attribute", "type"]
    _optional_keys = ["version", "prefixes"]

    def __init__(
        self,
        unique_name: str,
        dimension: str,
        attribute: str,
        type: str,
        version: str = None,
        prefixes: list[str] = None,
    ):
        """Represents a partition

        Args:
            unique_name (str): The name of the partition
            dimension (str): The dimension for the given partition
            attribute (str): The attribute for the given partition
            type (str): The type of the given partition
            version (str, optional): The version for the partition. Defaults to None.
            prefixes (list[str], optional): The prefixes for the partition. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.PARTITION
        self._unique_name = unique_name
        self._dimension = dimension
        self._attribute = attribute
        self._type = PartitionTypes(type)
        self._version = version
        self._prefixes = prefixes

        self._object_dict = {
            "unique_name": self._unique_name,
            "dimension": self._dimension,
            "attribute": self._attribute,
            "type": self._type.value,
        }
        if version is not None:
            self._object_dict["version"] = version
        if prefixes is not None:
            self._object_dict["prefixes"] = prefixes

    @property
    def dimension(self) -> str:
        """Getter for the dimension instance variable

        Returns:
            str: The dimension of this partition
        """
        return self._dimension

    @dimension.setter
    def dimension(
        self,
        value,
    ):
        """Setter for the dimension instance variable. This variable is final, you must construct a new PartitionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dimension is final; it cannot be altered."
        )

    @property
    def attribute(self) -> str:
        """Getter for the attribute instance variable

        Returns:
            str: The attribute of this partition
        """
        return self._attribute

    @attribute.setter
    def attribute(
        self,
        value,
    ):
        """Setter for the attribute instance variable. This variable is final, you must construct a new PartitionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of attribute is final; it cannot be altered."
        )

    @property
    def type(self) -> PartitionTypes:
        """Getter for the type instance variable

        Returns:
            PartitionTypes: The type of this partition
        """
        return self._type

    @type.setter
    def type(
        self,
        value,
    ):
        """Setter for the type instance variable. This variable is final, you must construct a new PartitionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of type is final; it cannot be altered."
        )

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of this partition
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new PartitionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def prefixes(self) -> str:
        """Getter for the prefixes instance variable

        Returns:
            str: The prefixes of this partition
        """
        return self._prefixes

    @prefixes.setter
    def prefixes(
        self,
        value,
    ):
        """Setter for the prefixes instance variable. This variable is final, you must construct a new PartitionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of prefixes is final; it cannot be altered."
        )
