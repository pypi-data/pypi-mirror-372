from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.level_object import LevelObject
from atscale.base.private_enums import SemanticObjectTypes


class HierarchyObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
        "levels",
    ]
    _optional_keys = [
        "description",
        "folder",
        "is_hidden",
    ]

    def __init__(
        self,
        unique_name: str,
        label: str,
        levels: List[LevelObject],
        description: str = None,
        folder: str = None,
        is_hidden: bool = False,
    ):
        """Organizes the attributes of its parent dimension into levels, where each level is a subdivision of the level
        above.

        Args:
            unique_name (str): the name of the hierarchy, how it will appear in queries
            label (str): the name of the hierarchy in BI tools
            levels (List[LevelObject]): The levels within the hierarchy.
            description (str, optional): the description of this hierarchy. Defaults to None to leave blank
            folder (str, optional): The name of the folder in which the hierarchy appears in BI tools.
            is_hidden (bool, optional): if the hierarchy should be hidden from BI tools. Defaults to False
        """
        self._object_type = SemanticObjectTypes.HIERARCHY
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._levels = levels

        self._description = description
        self._folder = folder
        self._is_hidden = is_hidden

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
            "levels": self._levels,
        }

        if description is not None:
            object_dict["description"] = self._description
        if folder is not None:
            object_dict["folder"] = self._folder
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden

        self._object_dict = object_dict

    @property
    def levels(self) -> List[LevelObject]:
        """Getter for the levels instance variable

        Returns:
            List[LevelObject]: The levels of this hierarchy
        """
        return self._levels

    @levels.setter
    def levels(
        self,
        value,
    ):
        """Setter for the levels instance variable. This variable is final, you must construct a new HierarchyObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of levels is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this hierarchy
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
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder of this hierarchy
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new HierarchyObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )

    @property
    def is_hidden(self) -> str:
        """Getter for the is_hidden instance variable

        Returns:
            str: The is_hidden of this hierarchy
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new Hierarchy.

        Args:
            value: setter cannot be used.
        """
        self._is_hidden = value
        self._object_dict["is_hidden"] = value

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
        level_attribute_ref: "LevelAttributeRef" = None,
    ) -> "HierarchyObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a HierarchyObject
            file_path (str): the file location of the source
            level_attribute_ref (LevelAttributeRef): The level attribute reference
            that this level calls out to. Defaults to None.
        Returns:
            HierarchyObject: a new hierarchy object
        """
        # `approved_dict` = required params + any optionals present in `object_dict`
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # convert semantic objects in approved dict to Pythonic representations
        ## parse levels
        approved_dict["levels"] = []

        for level in object_dict.get("levels", []):
            approved_dict["levels"].append(
                LevelObject.parse_dict(
                    object_dict=level,
                    file_path=file_path,
                    level_attribute_ref=level_attribute_ref,
                )
            )

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the hierarchy object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        # export levels
        ret_dict["levels"] = []
        for level in self._levels:
            ret_dict["levels"].append(level.to_export_dict())

        return ret_dict
