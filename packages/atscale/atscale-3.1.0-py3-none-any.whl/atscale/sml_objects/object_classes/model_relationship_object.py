from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes
from atscale.sml_objects.object_classes.dimension_relationship_reference_object import (
    DimensionRelationshipReferenceObject,
)
from atscale.sml_objects.object_classes.fact_relationship_reference_object import (
    FactRelationshipReferenceObject,
)
from atscale.utils.validation_utils import validate_role_play_format


class ModelRelationshipObject(SemanticObject):
    _required_keys = [
        "unique_name",
        "from",
        "to",
    ]
    _optional_keys = [
        "role_play",
    ]

    def __init__(
        self,
        unique_name: str,
        rel_from: FactRelationshipReferenceObject,
        rel_to: DimensionRelationshipReferenceObject,
        role_play: str = None,
    ):
        """Represents a model level relationship

        Args:
            unique_name (str): the dialect to apply the sql for
            rel_from (FactRelationshipReferenceObject): The fact dataset side of the relationship.
            rel_to (DimensionRelationshipReferenceObject): The dimension side of the relationship.
            role_play (str, optional): The role-playing template for the relationship. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.MODEL_RELATIONSHIP

        self._unique_name = unique_name
        self._rel_from = rel_from
        self._rel_to = rel_to

        object_dict = {
            "unique_name": self._unique_name,
            "from": self._rel_from,
            "to": self._rel_to,
        }

        if role_play is not None:
            validate_role_play_format(
                role_play=role_play,
            )

            self._role_play = role_play
            object_dict["role_play"] = self._role_play

        self._object_dict = object_dict

    @property
    def rel_from(self) -> FactRelationshipReferenceObject:
        """Getter for the rel_from instance variable

        Returns:
            FactRelationshipReferenceObject: The rel_from of this relationship
        """
        return self._rel_from

    @rel_from.setter
    def rel_from(
        self,
        value,
    ):
        """Setter for the rel_from instance variable. This variable is final, you must construct a new ModelRelationshipObject.

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
            DimensionRelationshipReferenceObject: The rel_to of this relationship
        """
        return self._rel_to

    @rel_to.setter
    def rel_to(
        self,
        value,
    ):
        """Setter for the rel_to instance variable. This variable is final, you must construct a new ModelRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of rel_to is final; it cannot be altered."
        )

    @property
    def role_play(self) -> str:
        """Getter for the role_play instance variable

        Returns:
            str: The role_play of this relationship
        """
        return self._role_play

    @role_play.setter
    def role_play(
        self,
        value,
    ):
        """Setter for the role_play instance variable. This variable is final, you must construct a new ModelRelationshipObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of role_play is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=dict,
        file_path=str,
    ) -> "ModelRelationshipObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a ModelRelationshipObject
            file_path (str): the file location of the source

        Returns:
            ModelRelationshipObject: a new model relationship object
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
            is_model_relationship=True,
        )

        # remove orignal names from the dict used for object construction
        for key in ["from", "to"]:
            del approved_dict[key]

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # now that we've constructed the object, change the name-protected keys back to
        # their original values in `object_dict`
        for key in ["from", "to"]:
            approved_dict[key] = approved_dict[f"rel_{key}"]
            del approved_dict[f"rel_{key}"]

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        return retObject

    def to_export_dict(self) -> dict:
        """Packs the values of the model relationship object back into a dictionary

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
