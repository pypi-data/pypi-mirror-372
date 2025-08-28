from copy import deepcopy
from typing import Dict, List

from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.base.private_enums import SemanticObjectTypes
from atscale.sml_objects.object_classes.dataset_properties_object import DatasetPropertiesObject


class CatalogObject(YamlObject):

    _required_keys = [
        "unique_name",
        "label",
        "version",
        "aggressive_agg_promotion",
        "build_speculative_aggs",
    ]
    _optional_keys = [
        "dataset_properties",
    ]

    def __init__(
        self,
        unique_name: str,
        version: str,
        label: str = None,
        aggressive_agg_promotion: bool = False,
        build_speculative_aggs: bool = False,
        dataset_properties: List[DatasetPropertiesObject] = None,
    ):
        """An object representing the control file for a given SML repository

        Args:
            unique_name (str): The name of the repository
            version (str): The version of SML being used
            label (str, optional): The name of the repository as it appears in the consumption tool. Defaults to None.
            aggressive_agg_promotion (bool, optional): Enables/disables aggressive aggregate promotion for the repository. Defaults to False
            build_speculative_aggs (bool, optional): Enables/disables speculative aggregates for the repository. Defaults to False
            dataset_properties (List[DatasetPropertiesObject], optional): Dataset properties to use within the repository. Defaults to None
        """

        self._object_type = SemanticObjectTypes.CATALOG
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._version = version
        self._aggressive_agg_promotion = aggressive_agg_promotion
        self._build_speculative_aggs = build_speculative_aggs
        self._dataset_properties = dataset_properties

        object_dict = {
            "unique_name": self._unique_name,
            "object_type": self._object_type.value,
            "label": self._label,
            "version": self._version,
            "aggressive_agg_promotion": self._aggressive_agg_promotion,
            "build_speculative_aggs": self._build_speculative_aggs,
        }

        self._object_dict = object_dict
        self._file_path = None

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The name of the repository as it appears in the consumption tool
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable.

        Args:
            value: The value to which label will be set.
        """
        self._label = value
        self._object_dict["label"] = value

    @property
    def version(self) -> str:
        """Getter for the version instance variable

        Returns:
            str: The version of SML being used
        """
        return self._version

    @version.setter
    def version(
        self,
        value,
    ):
        """Setter for the version instance variable. This variable is final, you must construct a new CatalogObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of version is final; it cannot be altered."
        )

    @property
    def aggressive_agg_promotion(self) -> bool:
        """Getter for the aggressive_agg_promotion instance variable

        Returns:
            bool: Enables/disables aggressive aggregate promotion for the repository
        """
        return self._aggressive_agg_promotion

    @aggressive_agg_promotion.setter
    def aggressive_agg_promotion(
        self,
        value,
    ):
        """Setter for the aggresive_agg_promotion instance variable.

        Args:
            value: The value to which aggressive_agg_promotion will be set.
        """
        self._aggressive_agg_promotion = value
        self._object_dict["aggressive_agg_promotion"] = value

    @property
    def build_speculative_aggs(self) -> bool:
        """Getter for the build_speculative_aggs instance variable

        Returns:
            bool: Enables/disables speculative aggregates for the repository
        """
        return self._build_speculative_aggs

    @build_speculative_aggs.setter
    def build_speculative_aggs(
        self,
        value,
    ):
        """Setter for the build_speculative_aggs instance variable.

        Args:
            value: The value to which build_speculative_aggs will be set.
        """
        self._build_speculative_aggs = value
        self._object_dict["build_speculative_aggs"] = value

    @property
    def dataset_properties(self) -> Dict:
        """Getter for the dataset_properties instance variable

        Returns:
            Dict: Dataset properties to use within the repository
        """
        return self._dataset_properties

    @dataset_properties.setter
    def dataset_properties(
        self,
        value,
    ):
        """Setter for the dataset_properties instance variable. This variable is final, you must construct a new CatalogObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset_properties is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "CatalogObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a CatalogObject
            file_path (str): the file location of the source
        Returns:
            CatalogObject: a new column object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict, req_keys=cls._required_keys, file_path=file_path
        )

        optionals_existing = {
            key: object_dict[key] for key in cls._optional_keys if key in object_dict
        }

        approved_dict.update(optionals_existing)

        if "dataset_properties" in object_dict:
            approved_dict["dataset_properties"] = []
            for dataset_prop in object_dict.get("dataset_properties", []):
                approved_dict["dataset_properties"].append(
                    DatasetPropertiesObject.parse_dict(dataset_prop, file_path)
                )

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the catalog object back into a dictionary
        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)
        if self._dataset_properties is not None:
            ret_dict["dataset_properties"] = []
            for dataset_prop in self._dataset_properties:
                ret_dict["dataset_properties"].append(dataset_prop.to_export_dict())
        return ret_dict
