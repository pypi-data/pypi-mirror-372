from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.utils import sml_io_utils
from atscale.sml_objects.yaml_object import YamlObject
from atscale.sml_objects.object_classes.hierarchy_object import HierarchyObject
from atscale.sml_objects.object_classes.level_attribute_object import (
    LevelAttributeObject,
)
from atscale.sml_objects.object_classes.dimension_relationship_object import (
    DimensionRelationshipObject,
)
from atscale.sml_objects.object_classes.calculation_group_object import (
    CalculationGroupObject,
)
from atscale.base.private_enums import SemanticObjectTypes, HierarchyTypes


class DimensionObject(YamlObject):
    _required_keys = [
        "unique_name",
        "label",
        "hierarchies",
        "level_attributes",
    ]
    _optional_keys = [
        "relationships",
        "calculation_groups",
        "description",
        "type",
    ]

    def __init__(
        self,
        unique_name: str,
        hierarchies: List[HierarchyObject],
        level_attributes: List["LevelAttributeObject"],
        label: str = None,
        relationships: List[DimensionRelationshipObject] = [],
        calculation_groups: List[CalculationGroupObject] = [],
        description: str = None,
        type: str = None,
    ):
        """A logical collection of attributes that are bound to specific columns in a source dataset.

        Args:
            unique_name (str): The unique name of the dimension.
            hierarchies (List[Hierarchy]): The hierarchies within the dimension.
            level_attributes (List[LevelAttribute]): The level attributes associated with hierarchies in this dimension.
            label (str, optional): The name of the dimension as it appears in the consumption tool. Defaults to None.
            relationships (List[Relationship]): The dimension's relationships. Defaults to [].
            calculation_groups (List[CalculationGroup]): The calculation groups to use in the dimension. Defaults to [].
            description (str, optional): The description of the dimension. Defaults to None.
            type (str, optional): The hierarchy type. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.DIMENSION
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._hierarchies = hierarchies
        self._level_attributes = level_attributes
        self._relationships = relationships
        self._calculation_groups = calculation_groups
        self._description = description

        if type is not None:
            self._type = HierarchyTypes(type)
        else:
            self._type = None

        object_dict = {
            "unique_name": self._unique_name,
            "object_type": self._object_type.value,
            "label": self._label,
            "hierarchies": self._hierarchies,
            "level_attributes": self._level_attributes,
        }
        if relationships is not None:
            object_dict["relationships"] = self._relationships
        if calculation_groups is not None:
            object_dict["calculation_groups"] = self._calculation_groups
        if description is not None:
            object_dict["description"] = self._description
        if type is not None:
            object_dict["type"] = self._type

        self._object_dict = object_dict
        self._file_path = None

    @property
    def hierarchies(self) -> List[HierarchyObject]:
        """Getter for the hierarchies instance variable.

        Returns:
            str: The hierarchies within the dimension.
        """
        return self._hierarchies

    @hierarchies.setter
    def hierarchies(
        self,
        value,
    ):
        """Setter for the hierarchies instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of hierarchies is final; it cannot be altered."
        )

    @property
    def level_attributes(self) -> List["LevelAttributeObject"]:
        """Getter for the level_attributes instance variable.

        Returns:
            str: The level attributes within the dimension.
        """
        return self._level_attributes

    @level_attributes.setter
    def level_attributes(
        self,
        value,
    ):
        """Setter for the level_attributes instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of level_attributes is final; it cannot be altered."
        )

    @property
    def relationships(self) -> List[DimensionRelationshipObject]:
        """Getter for the relationships instance variable.

        Returns:
            str: The relationships within the dimension.
        """
        return self._relationships

    @relationships.setter
    def relationships(
        self,
        value,
    ):
        """Setter for the relationships instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of relationships is final; it cannot be altered."
        )

    @property
    def calculation_groups(self) -> List[CalculationGroupObject]:
        """Getter for the calculation_groups instance variable.

        Returns:
            str: The calculation groups within the dimension.
        """
        return self._calculation_groups

    @calculation_groups.setter
    def calculation_groups(
        self,
        value,
    ):
        """Setter for the calculation_groups instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of calculation_groups is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable.

        Returns:
            str: The description of the dimension.
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: The value to which description will be set.
        """
        self._description = value
        self._object_dict["description"] = value

    @property
    def type(self) -> HierarchyTypes:
        """Getter for the type instance variable.

        Returns:
            HierarchyTypes: The type of the dimension.
        """
        return self._type

    @type.setter
    def type(
        self,
        value,
    ):
        """Setter for the type instance variable. This variable is final, you must construct a new DimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of type is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "DimensionObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a DimensionObject
            file_path (str): the file location of the source

        Returns:
            DimensionObject: a new dimension object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # read level attribute data into object that all subsequent level constructions can draw on
        level_attribute_object_dicts = object_dict.get("level_attributes", [])
        level_attributes = [
            LevelAttributeObject.parse_dict(
                object_dict=d,
                file_path=file_path,
            )
            for d in level_attribute_object_dicts
        ]

        approved_dict["level_attributes"] = level_attributes

        # construct reference to level attributes for HierarchyObject and LevelObject to use
        level_attribute_ref = sml_io_utils.LevelAttributeRef(
            level_attributes=level_attributes,
        )

        # parse hierarchies
        approved_dict["hierarchies"] = []

        for hierarchy in object_dict.get("hierarchies", []):
            # pass level attributes down to each hierarchy
            approved_dict["hierarchies"].append(
                HierarchyObject.parse_dict(
                    object_dict=hierarchy,
                    file_path=file_path,
                    level_attribute_ref=level_attribute_ref,
                )
            )

        # parse dimension relationships
        if "relationships" in object_dict:
            approved_dict["relationships"] = []

            for relationship in object_dict.get("relationships", []):
                approved_dict["relationships"].append(
                    DimensionRelationshipObject.parse_dict(
                        relationship,
                        file_path,
                    )
                )

        # parse calculation groups
        if "calculation_groups" in object_dict:
            approved_dict["calculation_groups"] = []

            for calculation_group in object_dict.get("calculation_groups", []):
                approved_dict["calculation_groups"].append(
                    CalculationGroupObject.parse_dict(
                        calculation_group,
                        file_path,
                    )
                )

        if "type" in object_dict:
            approved_dict["type"] = HierarchyTypes(object_dict["type"])

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict | approved_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the dimension object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        # export hierarchies
        ret_dict["hierarchies"] = []
        for hierarchy in self._hierarchies:
            ret_dict["hierarchies"].append(hierarchy.to_export_dict())

        # export level_attributes
        ret_dict["level_attributes"] = []
        for level_attribute in self._level_attributes:
            ret_dict["level_attributes"].append(level_attribute.to_export_dict())

        # export relationships
        if self._relationships != []:
            ret_dict["relationships"] = []
            for relationship in self._relationships:
                ret_dict["relationships"].append(relationship.to_export_dict())

        # export calculation groups
        if self._calculation_groups != []:
            ret_dict["calculation_groups"] = []
            for calculation_group in self._calculation_groups:
                ret_dict["calculation_groups"].append(calculation_group.to_export_dict())

        if ret_dict["type"] is not None:
            ret_dict["type"] = ret_dict["type"].value

        return ret_dict
