from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class DimensionRelationshipReferenceObject(SemanticObject):

    _required_keys = []
    _optional_keys = [
        "dimension",
        "level",
        "row_security",
    ]

    def __init__(
        self,
        is_model_relationship: bool,
        dimension: str = None,
        level: str = None,
        row_security: str = None,
    ):
        """The supported properties describing the `to` node of a dimension relationship.

        Args:
            is_model_relationship (bool): Whether this relationship exists on a model (the alternative being on a dimension).
            dimension (str, optional): The name of the dimension the `from` dataset is linked to. Defaults to None.
            level (str, optional): The key level within the dimension to use for the relationship. Defaults to None.
            row_security (str, optional): The row security relationship object the `from` dataset is linked to. Defaults to None.
        """

        if row_security is None:
            if is_model_relationship and (dimension is None or level is None):
                raise ValueError(
                    "`level` and `dimension` are required for model relationships if not a security dimension"
                )
            if not is_model_relationship and level is None:
                raise ValueError(
                    "`level` is required for dimension relationships if not a security dimension"
                )

        else:
            if level is not None or dimension is not None:
                raise ValueError(
                    "`row_security` or `level` and `dimension` can be passed to `DimensionRelationshipToObject`, not both"
                )

        self._object_type = SemanticObjectTypes.DIMENSION_RELATIONSHIP_REFERENCE
        self._dimension = dimension
        self._level = level
        self._row_security = row_security

        object_dict = {}
        if dimension is not None:
            object_dict["dimension"] = self._dimension
        if level is not None:
            object_dict["level"] = self._level
        if row_security is not None:
            object_dict["row_security"] = self._row_security
        self._object_dict = object_dict

    @property
    def dimension(self) -> str:
        """Getter for the dimension instance variable

        Returns:
            str: The dimension of this object
        """
        return self._dimension

    @dimension.setter
    def dimension(
        self,
        value,
    ):
        """Setter for the dimension instance variable. This variable is final, you must construct a new DimensionRelationshipToObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dimension is final; it cannot be altered."
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
        """Setter for the level instance variable. This variable is final, you must construct a new DimensionRelationshipToObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of level is final; it cannot be altered."
        )

    @property
    def row_security(self) -> str:
        """Getter for the row_security instance variable

        Returns:
            str: The row_security of this object
        """
        return self._row_security

    @row_security.setter
    def row_security(
        self,
        value,
    ):
        """Setter for the row_security instance variable. This variable is final, you must construct a new DimensionRelationshipToObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of row_security is final; it cannot be altered."
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

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
        is_model_relationship: bool,
    ) -> "DimensionRelationshipReferenceObject":
        """Parses a dictionary representation of a YAML object into a DimensionRelationshipReferenceObject

        Args:
            object_dict (Dict): the dictionary to unpack into a DimensionRelationshipReferenceObject
            file_path (str): the file location of the source
            is_model_relationship (bool): Whether this relationship exists on a model (the alternative being on a dimension).

        Returns:
            DimensionRelationshipReferenceObject: a new DimensionRelationshipReferenceObject object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        )

        optionals_existing = {
            key: object_dict[key] for key in cls._optional_keys if key in object_dict
        }

        # add `is_model_relationship` to object construction dictionary to induce different constructor behavior depending on
        # whether the relationship lives on a model or a dimensions

        approved_dict["is_model_relationship"] = is_model_relationship

        approved_dict.update(optionals_existing)
        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject
