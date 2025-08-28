from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes, RelationshipTypes
from atscale.sml_objects.object_classes.dimension_relationship_reference_object import (
    DimensionRelationshipReferenceObject,
)
from atscale.sml_objects.object_classes.fact_relationship_reference_object import (
    FactRelationshipReferenceObject,
)


class DimensionRelationshipObject(SemanticObject):

    _required_keys = [
        "from",
        "to",
        "type",
    ]
    _optional_keys = [
        "unique_name",
        "role_play",
    ]

    def __init__(
        self,
        rel_from: FactRelationshipReferenceObject,
        rel_to: DimensionRelationshipReferenceObject,
        rel_type: str,
        unique_name: str = None,
        role_play: str = None,
    ):
        """A class representing relationships to embedded/Snowflake dimensions.

        Args:
            rel_from (FactRelationshipReferenceObject): The dimension side of the relationship.
            rel_to (DimensionRelationshipReferenceObject): The fact side of the relationship.
            rel_type (str): Whether the relationship is either embedded or Snowflake.
            unique_name (str, optional): The name of the relationship. Defaults to None
            role_play (str, optional): The role-playing template for the relationship. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.DIMENSION_RELATIONSHIP

        self._rel_from = rel_from
        self._rel_to = rel_to
        self._rel_type = RelationshipTypes(rel_type)
        self._unique_name = unique_name
        self._role_play = role_play

        object_dict = {
            "from": self._rel_from,
            "to": self._rel_to,
            "type": self._rel_type.value,
        }

        if unique_name is not None:
            object_dict["unique_name"] = self._unique_name
        if role_play is not None:
            object_dict["role_play"] = self._role_play

        self._object_dict = object_dict

    @property
    def rel_from(self) -> FactRelationshipReferenceObject:
        """Getter for the rel_from instance variable

        Returns:
            FactRelationshipReferenceObject: The side of the relationship that contains the physical dataset that you want to connect to another dimension
        """
        return self._rel_from

    @rel_from.setter
    def rel_from(
        self,
        value,
    ):
        """Setter for the rel_from instance variable. This variable is final, you must construct a new DimensionRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of rel_from is final; it cannot be altered."
        )

    @property
    def rel_to(self) -> DimensionRelationshipReferenceObject:
        """Getter for the rel_to instance variable

        Returns:
            DimensionRelationshipReferenceObject: The object that the `rel_to` object is linked to.
        """
        return self._rel_to

    @rel_to.setter
    def rel_to(
        self,
        value,
    ):
        """Setter for the rel_to instance variable. This variable is final, you must construct a new DimensionRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of rel_to is final; it cannot be altered."
        )

    @property
    def rel_type(self) -> RelationshipTypes:
        """Getter for the rel_type instance variable

        Returns:
            RelationshipTypes: Whether the relationship is either embedded or snowflake.
        """
        return self._rel_type

    @rel_type.setter
    def rel_type(
        self,
        value,
    ):
        """Setter for the rel_type instance variable. This variable is final, you must construct a new DimensionRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of rel_type is final; it cannot be altered."
        )

    @property
    def role_play(self) -> str:
        """Getter for the role_play instance variable

        Returns:
            str: The role-playing template for the relationship
        """
        return self._role_play

    @role_play.setter
    def role_play(
        self,
        value,
    ):
        """Setter for the role_play instance variable. This variable is final, you must construct a new DimensionRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of role_play is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "DimensionRelationshipObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a DimensionRelationshipObject
            file_path (str): the file location of the source
        Returns:
            DimensionRelationshipObject: a new dimension relationship object
        """
        # `approved_dict` = required params + any optionals present in `object_dict`
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # convert semantic objects in approved dict to Pythonic representations
        ## parse fact relationship reference
        approved_dict["rel_from"] = FactRelationshipReferenceObject.parse_dict(
            object_dict=object_dict["from"],
            file_path=file_path,
        )

        ## parse dimension relationship reference
        approved_dict["rel_to"] = DimensionRelationshipReferenceObject.parse_dict(
            object_dict=object_dict["to"],
            file_path=file_path,
            is_model_relationship=False,
        )

        ## parse fact relationship type
        approved_dict["rel_type"] = approved_dict["type"]

        # remove orignal names from the dict used for object construction
        for key in ["from", "to", "type"]:
            del approved_dict[key]

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # now that we've constructed the object, change the name-protected keys back to
        # their original values in `object_dict`
        for key in ["from", "to", "type"]:
            approved_dict[key] = approved_dict[f"rel_{key}"]
            del approved_dict[f"rel_{key}"]

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the dimension relationship object back into a dictionary

        Returns:
            Dict: the output dictionary
        """
        ret_dict = deepcopy(self._object_dict)

        from_key = "from"
        to_key = "to"

        # set `from` dict
        ret_dict[from_key] = self._rel_from.to_export_dict()

        # get `to` dict
        ret_dict[to_key] = self._rel_to.to_export_dict()

        return ret_dict
