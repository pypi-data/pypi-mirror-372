from typing import Dict
from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class AttributeReferenceObject(SemanticObject):
    _required_keys = ["name", "dimension"]
    _optional_keys = ["partition", "distribution", "relationships_path"]

    def __init__(
        self,
        name: str,
        dimension: str,
        partition: str = None,
        distribution: str = None,
        relationships_path: list[str] = None,
    ):
        """Represents a attribute reference

        Args:
            name (str): the name of the attribute.
            dimension (str): the name of the attribute.
            partition (str, optional): the partition for the attribute. Defaults to None.
            distribution (str, optional): the distribution for the attribute. Defaults to None.
            relationships_path (list[str], optional): the relationships path for the attribute. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.ATTRIBUTE_REFERENCE
        self._name = name
        self._dimension = dimension
        self._partition = partition
        self._distribution = distribution
        self._relationships_path = relationships_path

        self._object_dict = {"name": name, "dimension": dimension}
        if partition is not None:
            self._object_dict["partition"] = partition
        if distribution is not None:
            self._object_dict["distribution"] = distribution
        if relationships_path is not None:
            self._object_dict["relationships_path"] = relationships_path

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The name of this metric
        """
        return self._name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, you must construct a new AttributeReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def dimension(self) -> str:
        """Getter for the dimension instance variable

        Returns:
            str: The dimension of this attribute reference
        """
        return self._dimension

    @dimension.setter
    def dimension(
        self,
        value,
    ):
        """Setter for the dimension instance variable. This variable is final, you must construct a new AttributeReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dimension is final; it cannot be altered."
        )

    @property
    def partition(self) -> str:
        """Getter for the partition instance variable

        Returns:
            str: The partition of this attribute reference
        """
        return self._partition

    @partition.setter
    def partition(
        self,
        value,
    ):
        """Setter for the partition instance variable. This variable is final, you must construct a new AttributeReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of partition is final; it cannot be altered."
        )

    @property
    def distribution(self) -> str:
        """Getter for the distribution instance variable

        Returns:
            str: The distribution of this attribute reference
        """
        return self._distribution

    @distribution.setter
    def dimension(
        self,
        value,
    ):
        """Setter for the distribution instance variable. This variable is final, you must construct a new AttributeReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of distribution is final; it cannot be altered."
        )

    @property
    def relationships_path(self) -> list[str]:
        """Getter for the relationships_path instance variable

        Returns:
            str: The relationships_path of this attribute reference
        """
        return self._relationships_path

    @relationships_path.setter
    def relationships_path(
        self,
        value,
    ):
        """Setter for the relationships_path instance variable. This variable is final, you must construct a new AttributeReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of relationships_path is final; it cannot be altered."
        )
