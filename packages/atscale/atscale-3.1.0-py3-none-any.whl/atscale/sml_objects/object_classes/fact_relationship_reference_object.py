from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class FactRelationshipReferenceObject(SemanticObject):

    _required_keys = [
        "dataset",
        "join_columns",
    ]
    _optional_keys = [
        "hierarchy",
        "level",
    ]

    def __init__(
        self,
        dataset: str,
        join_columns: List[str],
        hierarchy: str = None,
        level: str = None,
    ):
        """The supported properties describing the `from` node of a dimension relationship.

        Args:
            dataset (str): The physical dataset to which the dimension is linked
            join_columns (List[str]): The columns within the dataset used for the join
            hierarchy (str, optional): The hierarchy within the dimension from which the relationship originates. Defaults to None.
            level (str, optional): The level within the hierarchy from which the relationship originates. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.FACT_RELATIONSHIP_REFERENCE
        self._dataset = dataset
        self._join_columns = join_columns
        self._hierarchy = hierarchy
        self._level = level

        object_dict = {
            "dataset": self._dataset,
            "join_columns": self._join_columns,
        }
        if hierarchy is not None:
            object_dict["hierarchy"] = self._hierarchy
        if level is not None:
            object_dict["level"] = self._level

        self._object_dict = object_dict

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this object
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new DimensionRelationshipFromObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset is final; it cannot be altered."
        )

    @property
    def join_columns(self) -> str:
        """Getter for the join_columns instance variable

        Returns:
            str: The join_columns of this object
        """
        return self._join_columns

    @join_columns.setter
    def join_columns(
        self,
        value,
    ):
        """Setter for the join_columns instance variable. This variable is final, you must construct a new DimensionRelationshipFromObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of join_columns is final; it cannot be altered."
        )

    @property
    def hierarchy(self) -> str:
        """Getter for the hierarchy instance variable

        Returns:
            str: The hierarchy of this object
        """
        return self._hierarchy

    @hierarchy.setter
    def hierarchy(
        self,
        value,
    ):
        """Setter for the hierarchy instance variable. This variable is final, you must construct a new DimensionRelationshipFromObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of hierarchy is final; it cannot be altered."
        )

    @property
    def level(self) -> str:
        """Getter for the level instance variable

        Returns:
            str: The level of this object
        """
        return self._level

    @level.setter
    def level(
        self,
        value,
    ):
        """Setter for the level instance variable. This variable is final, you must construct a new DimensionRelationshipFromObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of level is final; it cannot be altered."
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
