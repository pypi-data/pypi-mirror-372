from copy import deepcopy
from enum import Enum

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.attribute_reference_object import (
    AttributeReferenceObject,
)
from atscale.base.private_enums import SemanticObjectTypes


class CachingEnum(Enum):
    ENGINE_MEMORY = "engine-memory"


class AggregateObject(SemanticObject):
    # target_connection was required but temporarily removed
    _required_keys = ["unique_name", "label"]
    _optional_keys = ["version", "attributes", "metrics", "caching"]

    def __init__(
        self,
        unique_name: str,
        metrics: list[str] = None,
        label: str = None,
        version: str = None,
        attributes: list[AttributeReferenceObject] = None,
        caching: CachingEnum = CachingEnum.ENGINE_MEMORY,
    ):
        """Represents a user defined aggregate

        Args:
            unique_name (str): The name of the aggregate.
            metrics (list[str], optional): The metrics in the aggregate. Defaults to None.
            label (str, optional): The label for the aggregate. Defaults to None.
            version (str, optional): The version for the aggregate. Defaults to None.
            attributes (list[AttributeReferenceObject], optional): The attributes for the aggregate. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.AGGREGATE
        self._unique_name = unique_name
        if not label:
            label = unique_name
        self._label = label
        self._metrics = metrics
        self._version = version
        self._attributes = attributes
        self._caching = caching

        self._object_dict = {"unique_name": self._unique_name, "label": self._label}
        # set anything that is not an object which will require its own export_dict method
        if metrics is not None:
            self._object_dict["metrics"] = metrics
        if version is not None:
            self._object_dict["version"] = version

    @property
    def metrics(self) -> list[str]:
        """Getter for the metrics instance variable

        Returns:
            str: The metrics of this aggregate
        """
        return self._metrics

    @metrics.setter
    def metrics(
        self,
        value,
    ):
        """Setter for the metrics instance variable. This variable is final, you must construct a new AggregateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of metrics is final; it cannot be altered."
        )

    @property
    def label(self) -> int:
        """Getter for the label instance variable

        Returns:
            str: The label of this aggregate
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. This variable is final, you must construct a new AggregateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sql is final; it cannot be altered."
        )

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of this aggregate
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new AggregateObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sql is final; it cannot be altered."
        )

    @property
    def attributes(self) -> list[AttributeReferenceObject]:
        """Getter for the attributes instance variable

        Returns:
            str: The attributes of this aggregate
        """
        return self._attributes

    @attributes.setter
    def attributes(
        self,
        value,
    ):
        """Setter for the attributes instance variable. This variable is final, you must construct a new AggregateObject.

        Args:
            value: setter attributes be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of attributes is final; it cannot be altered."
        )

    @property
    def caching(self) -> CachingEnum:
        """Getter for the caching instance variable

        Returns:
            CachingEnum: The caching of this aggregate
        """
        return self._caching

    @caching.setter
    def caching(self, value: CachingEnum):
        """Setter for the caching instance variable. This variable is final, you must construct a new AggregateObject."""
        raise atscale_errors.UnsupportedOperationException(
            "The value of caching is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=dict,
        file_path=str,
    ) -> "AggregateObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a AggregateObject
            file_path (str): the file location of the source

        Returns:
            AggregateObject: a new aggregate object
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

        if "attributes" in object_dict:
            approved_dict["attributes"] = []

            for attribute in object_dict.get("attributes", []):
                approved_dict["attributes"].append(
                    AttributeReferenceObject.parse_dict(attribute, file_path)
                )
        if "caching" in object_dict:
            approved_dict["caching"] = CachingEnum(object_dict.get("caching"))

        retObject = cls(**approved_dict)

        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> dict:
        """Packs the values of the aggregate object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        if self._attributes is not None:
            ret_dict["attributes"] = []
            for attribute in self._attributes:
                ret_dict["attributes"].append(attribute.to_export_dict())
        if self._caching is not None:
            ret_dict["caching"] = self._caching.value

        return ret_dict
