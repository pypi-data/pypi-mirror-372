from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class OverridesObject(SemanticObject):
    _required_keys = ["query_name"]
    _optional_keys = []

    def __init__(
        self,
        name_map: dict,
    ):
        """Represents a query name override

        Args:
            name_map (str): the mapping of name overrides
        """

        self._object_type = SemanticObjectTypes.OVERRIDES
        self._name_map = name_map

        self._object_dict = {}
        for key, value in name_map.items():
            self._object_dict[key] = {"query_name": value}

    @property
    def name_map(self) -> dict:
        """Getter for the name_map instance variable

        Returns:
            str: The name_map of this override
        """
        return self._name_map

    @name_map.setter
    def name_map(
        self,
        value,
    ):
        """Setter for the name_map instance variable. This variable is final, you must construct a new OverridesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name_map is final; it cannot be altered."
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
    def parse_dict(cls, object_dict: dict, file_path: str) -> "OverridesObject":
        """

        Args:
            object_dict (Dict): the dictionary to unpack into a OverridesObject
            file_path (str): the file location of the source

        Returns:
            OverridesObject: a new overrides object
        """
        name_map = {}
        for key, value in object_dict.items():
            dct = cls._get_required(
                inbound_dict=value,
                req_keys=cls._required_keys,
                file_path=file_path,
            )
            name_map[key] = dct["query_name"]

        retObject = cls(name_map=name_map)  # constructs just for setting the name map
        retObject._object_dict = deepcopy(object_dict)  # stores the original object_dict to save unknown fields

        return retObject
