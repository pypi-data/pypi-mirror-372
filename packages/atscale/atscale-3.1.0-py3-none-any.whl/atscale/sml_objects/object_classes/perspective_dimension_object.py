from copy import deepcopy
from typing import Dict
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes
from atscale.sml_objects.object_classes.perspective_hierarchy_object import (
    PerspectiveHierarchyObject,
)


class PerspectiveDimensionObject(SemanticObject):
    _required_keys = ["name"]
    _optional_keys = [
        "prefixes",
        "hierarchies",
        "secondary_attributes",
    ]

    def __init__(
        self,
        name: str,
        prefixes: list[str] = None,
        secondary_attributes: list[str] = None,
        hierarchies: list[PerspectiveHierarchyObject] = None,
    ):
        """Represents a perspective dimension

        Args:
            name (str): the name of the dimension
            prefixes (list[str], optional): the prefixes for the dimension. Defaults to None.
            secondary_attributes (list[str], optional): the secondary attributes for the dimension. Defaults to None.
            hierarchies (list[PerspectiveHierarchyObject], optional): the hierarchies for the dimension. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.PERSPECTIVE_DIMENSION
        self._name = name
        self._prefixes = prefixes
        self._secondary_attributes = secondary_attributes
        self._hierarchies = hierarchies

        self._object_dict = {
            "name": self._name,
        }

        if prefixes is not None:
            self._object_dict["prefixes"] = prefixes
        if secondary_attributes is not None:
            self._object_dict["secondary_attributes"] = secondary_attributes
        if hierarchies is not None:
            self._object_dict["hierarchies"] = hierarchies

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The name of this dimension
        """
        return self._name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, you must construct a new PerspectiveDimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def prefixes(self) -> list[str]:
        """Getter for the prefixes instance variable

        Returns:
            str: The prefixes of this dimension
        """
        return self._prefixes

    @prefixes.setter
    def prefixes(
        self,
        value,
    ):
        """Setter for the prefixes instance variable. This variable is final, you must construct a new PerspectiveDimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of prefixes is final; it cannot be altered."
        )

    @property
    def secondary_attributes(self) -> list[str]:
        """Getter for the secondary_attributes instance variable

        Returns:
            str: The secondary_attributes of this dimension
        """
        return self._secondary_attributes

    @secondary_attributes.setter
    def secondary_attributes(
        self,
        value,
    ):
        """Setter for the secondary_attributes instance variable. This variable is final, you must construct a new PerspectiveDimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of secondary_attributes is final; it cannot be altered."
        )

    @property
    def hierarchies(self) -> list[PerspectiveHierarchyObject]:
        """Getter for the hierarchies instance variable

        Returns:
            str: The hierarchies of this dimension
        """
        return self._hierarchies

    @hierarchies.setter
    def hierarchies(
        self,
        value,
    ):
        """Setter for the hierarchies instance variable. This variable is final, you must construct a new PerspectiveDimensionObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of hierarchies is final; it cannot be altered."
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
    ) -> "PerspectiveDimensionObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a PerspectiveDimensionObject
            file_path (str): the file location of the source
        Returns:
            PerspectiveDimensionObject: a new perspective dimension object
        """
        # `approved_dict` = required params + any optionals present in `object_dict`
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # convert semantic objects in approved dict to Pythonic representations
        ## parse hierarchies, if any
        if "hierarchies" in object_dict:
            approved_dict["hierarchies"] = []

            for hierarchy in object_dict.get("hierarchies", []):
                approved_dict["hierarchies"].append(
                    PerspectiveHierarchyObject.parse_dict(
                        object_dict=hierarchy,
                        file_path=file_path,
                    )
                )

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        return retObject

    def to_export_dict(self) -> dict:
        """Packs the values of the perspective dimension object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        if self._hierarchies is not None:
            ret_dict["hierarchies"] = []
            for attribute in self._hierarchies:
                ret_dict["hierarchies"].append(attribute.to_export_dict())

        return ret_dict
