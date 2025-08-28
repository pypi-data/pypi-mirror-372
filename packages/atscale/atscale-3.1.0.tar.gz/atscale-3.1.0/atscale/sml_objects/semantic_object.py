from abc import abstractmethod
from abc import ABC, abstractmethod
from typing import Dict, List

from atscale.errors import atscale_errors
from atscale.base.private_enums import SemanticObjectTypes


class SemanticObject(ABC):
    """An abstract base class for our semantic object classes. Outlines some common functionality that
    all such classes should implement."""

    @abstractmethod
    def __init__(
        self,
    ):
        """Constructor for the class."""
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_export_dict() == other.to_export_dict()

    @property
    def unique_name(self) -> str:
        """Getter for the unique_name instance variable

        Returns:
            str: The unique_name of this metric
        """
        return self._unique_name

    @unique_name.setter
    def unique_name(
        self,
        value,
    ):
        """Setter for the unique_name instance variable. This variable is final, you must construct a new Metric.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of unique_name is final; it cannot be altered."
        )

    @property
    def object_type(
        self,
    ) -> SemanticObjectTypes:
        """The type of the semantic object as represented in SML.

        Returns:
            SemanticObjectTypes: A string containing the type of the semantic object as represented in SML.
        """
        return self._object_type

    @object_type.setter
    def object_type(
        self,
        value,
    ):
        """Setter for the object_type instance variable. This variable is final, please construct a new SemanticObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of object_type is final; it cannot be altered."
        )

    @property
    def object_dict(self) -> str:
        """Getter for the object_dict instance variable

        Returns:
            Dict: The object_dict of this metric
        """
        return self._object_dict

    @object_dict.setter
    def object_dict(
        self,
        value,
    ):
        """Setter for the object_dict instance variable. This variable is final, you must construct a new Metric.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of object_dict is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "SemanticObject":
        """Parses a dictionary representation of a YAML object into a SemanticObject

        Args:
            object_dict (Dict): the dictionary to unpack into a SemanticObject
            file_path (str): the file location of the source

        Returns:
            SemanticObject: a new SemanticObject object
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
        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(
        self,
    ) -> Dict:
        """Returns a dictionary of strings describing the semantic object which can be written back to .yml format.

        Returns:
            Dict: A dictionary of strings describing the semantic object.
        """
        return self._object_dict

    @staticmethod
    def _get_required(
        inbound_dict: Dict,
        req_keys: List[str],
        file_path: str,
    ) -> Dict:
        """gets a required key from the input dict, raises an error if the key is not present

        Args:
            inbound_dict (Dict):
            req_key (str):
            file_path (str):
        """
        ret_dict = {}
        for req_key in req_keys:

            ret_obj = inbound_dict.get(req_key, None)

            if ret_obj is None:
                raise ValueError(f"Required parameter {req_key} not found in file: {file_path}")
            ret_dict[req_key] = ret_obj

        return ret_dict
