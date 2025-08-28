from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes
from atscale.sml_objects.object_classes.perspective_dimension_object import (
    PerspectiveDimensionObject,
)


class PerspectiveObject(SemanticObject):
    _required_keys = ["unique_name"]
    _optional_keys = [
        "version",
        "dimensions",
        "metrics",
    ]

    def __init__(
        self,
        unique_name: str,
        version: str = None,
        metrics: list[str] = None,
        dimensions: list[PerspectiveDimensionObject] = None,
    ):
        """Represents a alternatice sql for an object

        Args:
            unique_name (str): the name of the perspective
            version (str, optional): the version of the perspective. Defaults to None.
            metrics (list[str], optional): the metrics of the perspective. Defaults to None.
            dimensions (list[PerspectiveDimensionObject], optional): the dimensions of the perspective. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.PERSPECTIVE
        self._unique_name = unique_name
        self._version = version
        self._metrics = metrics
        self._dimensions = dimensions

        self._object_dict = {"unique_name": self._unique_name}

        if version is not None:
            self._object_dict["version"] = version
        if metrics is not None:
            self._object_dict["metrics"] = metrics
        if dimensions is not None:
            self._object_dict["dimensions"] = dimensions

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of this perspective
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new PerspectiveObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def version(self) -> int:
        """Getter for the version instance variable

        Returns:
            str: The version of this perspective
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new PerspectiveObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def metrics(self) -> list[str]:
        """Getter for the metrics instance variable

        Returns:
            str: The metrics of this perspective
        """
        return self._metrics

    @metrics.setter
    def metrics(
        self,
        value,
    ):
        """Setter for the metrics instance variable. This variable is final, you must construct a new PerspectiveObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of metrics is final; it cannot be altered."
        )

    @property
    def dimensions(self) -> list[PerspectiveDimensionObject]:
        """Getter for the dimensions instance variable

        Returns:
            str: The dimensions of this perspective
        """
        return self._dimensions

    @dimensions.setter
    def dimensions(
        self,
        value,
    ):
        """Setter for the dimensions instance variable. This variable is final, you must construct a new PerspectiveObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dimensions is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=dict,
        file_path=str,
    ) -> "PerspectiveObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a PerspectiveObject
            file_path (str): the file location of the source

        Returns:
            PerspectiveObject: a new perspective object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # convert semantic objects in approved dict to Pythonic representations
        ## parse dimensions, if any
        if "dimensions" in object_dict:
            approved_dict["dimensions"] = []

            for dimension in object_dict.get("dimensions", []):
                approved_dict["dimensions"].append(
                    PerspectiveDimensionObject.parse_dict(
                        object_dict=dimension,
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
        """Packs the values of the perspective object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)

        if self._dimensions is not None:
            ret_dict["dimensions"] = []
            for attribute in self._dimensions:
                ret_dict["dimensions"].append(attribute.to_export_dict())

        return ret_dict
