from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.calculated_member_object import CalculatedMemberObject
from atscale.base.private_enums import SemanticObjectTypes


class CalculationGroupObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
        "calculated_members",
    ]
    _optional_keys = [
        "description",
        "folder",
    ]

    def __init__(
        self,
        unique_name: str,
        calculated_members: List[CalculatedMemberObject],
        label: str = None,
        description: str = None,
        folder: str = None,
    ):
        """A class representing the calculation groups to use in a given dimension.

        Args:
            unique_name (str): The name of this calculation group
            calculated_members (List[CalculatedMemberObject]): The individual calculations in the group
            label (str, optional): The name of this calculation group as it appears in consumption tools. Defaults to None.
            description (str, optional): The description of this calculation group. Defaults to None
            folder (str, optional): The folder in which the calculation group is stored. Defaults to None
        """

        self._object_type = SemanticObjectTypes.CALCULATION_GROUP
        self._unique_name = unique_name
        if not label:
            label = unique_name
        self._label = label
        self._calculated_members = calculated_members
        self._description = description
        self._folder = folder

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
            "calculated_members": self._calculated_members,
        }
        if description is not None:
            object_dict["description"] = self._description
        if folder is not None:
            object_dict["folder"] = self._folder

        self._object_dict = object_dict

    @property
    def calculated_members(self) -> List[CalculatedMemberObject]:
        """Getter for the calculated_members instance variable

        Returns:
            List[CalculatedMemberObject]: The individual calculations in the group
        """
        return self._calculated_members

    @calculated_members.setter
    def calculated_members(
        self,
        value,
    ):
        """Setter for the calculated_members instance variable. This variable is final, you must construct a new CalculationGroupObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of calculated_members is final; it cannot be altered."
        )

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The name of this calculation group as it appears in consumption tools
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable

        Args:
            value: The value to which label will be set
        """
        self._label = value
        self._object_dict["label"] = value

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this calculation group
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable

        Args:
            value: The value to which description will be set
        """
        self._description = value
        self._object_dict["description"] = value

    @property
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder in which the calculation group is stored
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new CalculationGroupObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=Dict,
        file_path=str,
    ) -> "CalculationGroupObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a CalculationGroupObject
            file_path (str): the file location of the source

        Returns:
            CalculationGroupObject: a new calculation group object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        )

        optionals_existing = {
            key: object_dict[key] for key in cls._optional_keys if key in object_dict
        }

        approved_dict.update(optionals_existing)

        # parse calculated_members
        approved_dict["calculated_members"] = []

        for calculated_member in object_dict.get("calculated_members", []):
            approved_dict["calculated_members"].append(
                CalculatedMemberObject.parse_dict(
                    calculated_member,
                    file_path,
                )
            )

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the calculation group object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        # export calculated_members
        ret_dict["calculated_members"] = []
        for calculated_member in self._calculated_members:
            ret_dict["calculated_members"].append(calculated_member.to_export_dict())

        return ret_dict
