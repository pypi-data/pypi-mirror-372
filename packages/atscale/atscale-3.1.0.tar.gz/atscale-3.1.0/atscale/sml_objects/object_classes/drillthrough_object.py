from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.attribute_reference_object import AttributeReferenceObject
from atscale.base.private_enums import SemanticObjectTypes


class DrillthroughObject(SemanticObject):
    _required_keys = ["unique_name", "metrics"]
    _optional_keys = ["notes", "version", "attributes"]

    def __init__(
        self,
        unique_name: str,
        metrics: list[str],
        notes: str = None,
        version: str = None,
        attributes: list[AttributeReferenceObject] = None,
    ):
        """Represents a drillthrough

        Args:
            unique_name (str): The name of the drillthrough.
            metrics (list[str]): The metrics in the drillthrough.
            version (str, optional): The version for the drillthrough. Defaults to None.
            attributes (list[AttributeReferenceObject], optional): The attributes for the drillthrough. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.DRILLTHROUGH
        self._unique_name = unique_name
        self._metrics = metrics
        self._notes = notes
        self._version = version
        self._attributes = attributes

        self._object_dict = {
            "unique_name": self._unique_name,
            "metrics": self._metrics,
        }

        if notes is not None:
            self._object_dict["notes"] = notes

        if version is not None:
            self._object_dict["version"] = version

    @property
    def metrics(self) -> list[str]:
        """Getter for the metrics instance variable

        Returns:
            str: The metrics of this drillthrough
        """
        return self._metrics

    @metrics.setter
    def metrics(
        self,
        value,
    ):
        """Setter for the metrics instance variable. This variable is final, you must construct a new DrillthroughObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of metrics is final; it cannot be altered."
        )

    @property
    def notes(self) -> str:
        """Getter for the notes instance variable

        Returns:
            str: Notes for this drillthrough
        """
        return self._notes

    @notes.setter
    def notes(
        self,
        value,
    ):
        """Setter for the notes instance variable. This variable is final, you must construct a new DrillthroughObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of notes is final; it cannot be altered."
        )

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of this drillthrough
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new DrillthroughObject.

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
            str: The attributes of this drillthrough
        """
        return self._attributes

    @attributes.setter
    def attributes(
        self,
        value,
    ):
        """Setter for the attributes instance variable. This variable is final, you must construct a new DrillthroughObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of attributes is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=dict,
        file_path=str,
    ) -> "DrillthroughObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a DrillthroughObject
            file_path (str): the file location of the source

        Returns:
            DrillthroughObject: a new drillthrough object
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

        retObject = cls(**approved_dict)

        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> dict:
        """Packs the values of the drillthrough object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        if self._attributes is not None:
            ret_dict["attributes"] = []
            for attribute in self._attributes:
                ret_dict["attributes"].append(attribute.to_export_dict())

        return ret_dict
