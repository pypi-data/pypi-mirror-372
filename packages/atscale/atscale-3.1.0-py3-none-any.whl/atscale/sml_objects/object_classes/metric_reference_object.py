from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class MetricReferenceObject(SemanticObject):
    _required_keys = ["unique_name"]
    _optional_keys = ["folder"]

    def __init__(self, unique_name: str, folder: str = None):
        """Represents a metric reference

        Args:
            unique_name (str): the name of the metric.
            folder (str, optional): the folder for the metric. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.METRIC_REFERENCE
        self._unique_name = unique_name
        self._folder = folder

        self._object_dict = {"unique_name": unique_name}
        if folder is not None:
            self._object_dict["folder"] = folder

    @property
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder of this metric reference
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new MetricReferenceObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )
