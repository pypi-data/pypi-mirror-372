from typing import Dict, List
from copy import deepcopy

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.alias_object import AliasObject
from atscale.sml_objects.object_classes.metrical_attribute_object import (
    MetricalAttributeObject,
)
from atscale.sml_objects.object_classes.secondary_attribute_object import (
    SecondaryAttributeObject,
)
from atscale.sml_objects.object_classes.parallel_period_object import ParallelPeriodObject
from atscale.base.private_enums import SemanticObjectTypes


class LevelObject(SemanticObject):

    _required_keys = [
        "unique_name",
    ]
    _optional_keys = [
        "secondary_attributes",
        "aliases",
        "metrics",
        "parallel_periods",
    ]

    def __init__(
        self,
        unique_name: str,
        secondary_attributes: List[SecondaryAttributeObject] = [],
        aliases: List[AliasObject] = [],
        metrics: List[MetricalAttributeObject] = [],
        parallel_periods: List[ParallelPeriodObject] = [],
        level_attribute_ref: "LevelAttributeRef" = None,
    ):
        """Represents a level of a given hierarchy.

        Args:
            unique_name (str): the name of the level, how it will appear in queries
            secondary_attributes (List[SecondaryAttributeObject], optional): Defines secondary attributes for the dimension level. Defaults to [].
            aliases (List[AliasObject], optional): Defines secondary attributes that can be used as aliases for specific hierarchy levels within BI tools. Defaults to [].
            metrics (List[MetricalAttributeObject], optional): Defines metrics for the level. Defaults to [].
            parallel_periods (List[ParallelPeriodObject], optional): Defines parallel periods for the level. Defaults to [].
            level_attribute_ref (LevelAttributeRef): The level attribute reference this object uses. Defaults to None.
        """
        self._object_type = SemanticObjectTypes.LEVEL
        self._unique_name = unique_name
        self._secondary_attributes = secondary_attributes
        self._aliases = aliases
        self._metrics = metrics
        self._parallel_periods = parallel_periods

        # NOTE: This object enables read/write of level attributes from this `LevelObject`. It is NOT designed to
        # be stored in this object's `object_dict` and/or be exposed via the export dict.
        self._level_attribute_ref = level_attribute_ref

        object_dict = {
            "unique_name": self._unique_name,
        }
        if secondary_attributes is not None:
            object_dict["secondary_attributes"] = self._secondary_attributes
        if aliases is not None:
            object_dict["aliases"] = self._aliases
        if metrics is not None:
            object_dict["metrics"] = self._metrics
        if parallel_periods is not None:
            object_dict["parallel_periods"] = self._parallel_periods

        self._object_dict = object_dict

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this level
        """
        return self._level_attribute_ref._ref.get(self._unique_name).label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable

        Args:
            value: The value to which label will be set
        """
        self._level_attribute_ref._ref.get(self._unique_name).label = value
        self._level_attribute_ref._ref.get(self._unique_name)._object_dict["label"] = value

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this level
        """
        return self._level_attribute_ref._ref.get(self._unique_name).dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset is final; it cannot be altered."
        )

    @property
    def name_column(self) -> str:
        """Getter for the name_column instance variable

        Returns:
            str: The column whose values appear for this level in the consumption tool
        """
        return self._level_attribute_ref._ref.get(self._unique_name).name_column

    @name_column.setter
    def name_column(
        self,
        value,
    ):
        """Setter for the name_column instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name_column is final; it cannot be altered."
        )

    @property
    def key_columns(self) -> List[str]:
        """Getter for the key_columns instance variable

        Returns:
            List[str]: The dataset column that the level is based on (all columns listed for compound keys)
        """
        return self._level_attribute_ref._ref.get(self._unique_name).key_columns

    @key_columns.setter
    def key_columns(
        self,
        value,
    ):
        """Setter for the key_columns instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_columns is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of the level
        """
        return self._level_attribute_ref._ref.get(self._unique_name).description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable.

        Args:
            value: The value to which description will be set
        """
        self._level_attribute_ref._ref.get(self._unique_name).description = value
        self._level_attribute_ref._ref.get(self._unique_name)._object_dict["description"] = value

    @property
    def is_hidden(self) -> bool:
        """Getter for the is_hidden instance variable

        Returns:
            bool: Whether the level is visible in consumption tools
        """
        return self._level_attribute_ref._ref.get(self._unique_name).is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )

    @property
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder of the level
        """
        return self._level_attribute_ref._ref.get(self._unique_name).folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of folder is final; it cannot be altered."
        )

    @property
    def time_unit(self) -> str:
        """Getter for the time_unit instance variable

        Returns:
            str: The unit of time to use (for time dimensions only).
        """
        return self._level_attribute_ref._ref.get(self._unique_name).time_unit

    @time_unit.setter
    def time_unit(
        self,
        value,
    ):
        """Setter for the time_unit instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of time_unit is final; it cannot be altered."
        )

    @property
    def secondary_attributes(
        self,
    ) -> List[SecondaryAttributeObject]:
        """Getter for the secondary_attributes instance variable

        Returns:
            List[SecondaryAttributeObject]: The secondary attributes of this level
        """
        return self._secondary_attributes

    @secondary_attributes.setter
    def secondary_attributes(
        self,
        value,
    ):
        """Setter for the secondary_attributes instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of secondary_attributes is final; it cannot be altered."
        )

    @property
    def aliases(
        self,
    ) -> List[AliasObject]:
        """Getter for the aliases instance variable

        Returns:
            List[AliasObject]: The aliases of this level
        """
        return self._aliases

    @aliases.setter
    def aliases(
        self,
        value,
    ):
        """Setter for the aliases instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of aliases is final; it cannot be altered."
        )

    @property
    def metrics(
        self,
    ) -> List[MetricalAttributeObject]:
        """Getter for the metrics instance variable

        Returns:
            List[MetricalAttributeObject]: The metrics of this level
        """
        return self._metrics

    @metrics.setter
    def metrics(
        self,
        value,
    ):
        """Setter for the metrics instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of metrics is final; it cannot be altered."
        )

    @property
    def parallel_periods(
        self,
    ) -> List[ParallelPeriodObject]:
        """Getter for the parallel_periods instance variable

        Returns:
            List[ParallelPeriodObject]: The parallel periods of this level
        """
        return self._parallel_periods

    @parallel_periods.setter
    def parallel_periods(
        self,
        value,
    ):
        """Setter for the parallel_periods instance variable. This variable is final, you must construct a new LevelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of parallel_periods is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
        level_attribute_ref: "LevelAttributeRef" = None,
    ) -> "LevelObject":
        """
        Args:
            object_dict (Dict): The dictionary to unpack into a LevelObject
            file_path (str): The file location of the source
            level_attribute_ref (LevelAttributeRef): The level attribute reference
            that this level calls out to. Defaults to None.

        Returns:
            LevelObject: a new level object
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

        # parse secondary attributes, if any
        if "secondary_attributes" in object_dict:
            approved_dict["secondary_attributes"] = []

            for secondary_attribute in object_dict.get("secondary_attributes", []):
                approved_dict["secondary_attributes"].append(
                    SecondaryAttributeObject.parse_dict(secondary_attribute, file_path)
                )

        # parse aliases, if any
        if "aliases" in object_dict:
            approved_dict["aliases"] = []

            for alias in object_dict.get("aliases", []):
                approved_dict["aliases"].append(AliasObject.parse_dict(alias, file_path))

        # parse metrics, if any
        if "metrics" in object_dict:
            approved_dict["metrics"] = []

            for metric in object_dict.get("metrics", []):
                approved_dict["metrics"].append(
                    MetricalAttributeObject.parse_dict(metric, file_path)
                )

        # parse parallel periods, if any
        if "parallel_periods" in object_dict:
            approved_dict["parallel_periods"] = []

            for parallel_period in object_dict.get("parallel_periods", []):
                approved_dict["parallel_periods"].append(
                    ParallelPeriodObject.parse_dict(parallel_period, file_path)
                )

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict
        retObject._level_attribute_ref = level_attribute_ref

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the level object back into a dictionary

        Returns:
            Dict: the output dictionary
        """
        ret_dict = deepcopy(self._object_dict)

        if self._secondary_attributes != []:
            ret_dict["secondary_attributes"] = []
            for secondary_attribute in self._secondary_attributes:
                ret_dict["secondary_attributes"].append(secondary_attribute.to_export_dict())

        if self._aliases != []:
            ret_dict["aliases"] = []
            for alias in self._aliases:
                ret_dict["aliases"].append(alias.to_export_dict())

        if self._metrics != []:
            ret_dict["metrics"] = []
            for metric in self._metrics:
                ret_dict["metrics"].append(metric.to_export_dict())

        if self._parallel_periods != []:
            ret_dict["parallel_periods"] = []
            for parallel_period in self._parallel_periods:
                ret_dict["parallel_periods"].append(parallel_period.to_export_dict())

        return ret_dict
