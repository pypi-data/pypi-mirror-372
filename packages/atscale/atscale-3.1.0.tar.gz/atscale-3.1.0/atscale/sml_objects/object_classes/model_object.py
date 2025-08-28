from typing import Dict
from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.sml_objects.object_classes.aggregate_object import AggregateObject
from atscale.sml_objects.object_classes.dataset_properties_object import DatasetPropertiesObject
from atscale.sml_objects.object_classes.drillthrough_object import DrillthroughObject
from atscale.sml_objects.object_classes.metric_reference_object import MetricReferenceObject
from atscale.sml_objects.object_classes.model_relationship_object import ModelRelationshipObject
from atscale.sml_objects.object_classes.overrides_object import OverridesObject
from atscale.sml_objects.object_classes.partition_object import PartitionObject
from atscale.sml_objects.object_classes.perspective_object import PerspectiveObject
from atscale.base.private_enums import SemanticObjectTypes


class ModelObject(YamlObject):
    _required_keys = ["unique_name", "label", "relationships", "metrics"]
    _optional_keys = [
        "dimensions",
        "description",
        "include_default_drillthrough",
        "aggregates",
        "perspectives",
        "drillthroughs",
        "partitions",
        "overrides",
        "dataset_properties",
    ]

    def __init__(
        self,
        unique_name: str,
        relationships: list[ModelRelationshipObject],
        metrics: list[MetricReferenceObject],
        label: str = None,
        description: str = None,
        dimensions: list[str] = None,
        aggregates: list[AggregateObject] = None,
        perspectives: list[PerspectiveObject] = None,
        drillthroughs: list[DrillthroughObject] = None,
        partitions: list[PartitionObject] = None,
        overrides: OverridesObject = None,
        dataset_properties: list[DatasetPropertiesObject] = None,
        include_default_drillthrough: bool = None,
    ):
        """Represents a semantic model

        Args:
            unique_name (str): the name of the metric, how it will appear in queries
            relationships: list[ModelRelationshipObject], optional): The relationships for the model.
            metrics: list[MetricReference]): The metrics for the model.
            label (str, optional): The label of the model. Defaults to None to match the unique_name.
            description (str, optional): The description of the model. Defaults to None.
            dimensions (list[str], optional): The dimensions for the model. Defaults to None.
            aggregates (list[AggregatesObject], optional): The aggregates for the model. Defaults to None.
            perspectives (list[PerspectiveObject], optional): The perspectives for the model. Defaults to None.
            drillthroughs (list[DrillthroughObject], optional): The drillthroughs for the model. Defaults to None.
            partitions (list[PartitionObject], optional): The partitions for the model. Defaults to None.
            overrides (OverridesObject, optional): The overrides for the model. Defaults to None.
            dataset_properties (list[DatasetPropertiesObject], optional): The dataset properties for the model. Defaults to None.
            include_default_drillthrough (bool, optional): . Defaults to None.
        """
        self._object_type = SemanticObjectTypes.MODEL
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._relationships = relationships
        self._metrics = metrics
        self._description = description
        self._dimensions = dimensions
        self._aggregates = aggregates
        self._perspectives = perspectives
        self._drillthroughs = drillthroughs
        self._partitions = partitions
        self._overrides = overrides
        self._dataset_properties = dataset_properties
        self._include_default_drillthrough = include_default_drillthrough
        self._description = description

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
            "object_type": self._object_type.value,
            "relationships": self._relationships,
            "metrics": self._metrics,
        }
        if description is not None:
            object_dict["description"] = self._description
        if dimensions is not None:
            object_dict["dimensions"] = self._dimensions
        if aggregates is not None:
            object_dict["aggregates"] = self._aggregates
        if perspectives is not None:
            object_dict["perspectives"] = self._perspectives
        if drillthroughs is not None:
            object_dict["drillthroughs"] = self._drillthroughs
        if partitions is not None:
            object_dict["partitions"] = self._partitions
        if overrides is not None:
            object_dict["overrides"] = self._overrides
        if dataset_properties is not None:
            object_dict["dataset_properties"] = self._dataset_properties
        if include_default_drillthrough is not None:
            object_dict["include_default_drillthrough"] = self._include_default_drillthrough

        self._object_dict = object_dict
        self._file_path = None

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this model
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable.

        Args:
            value: The value to which description will be set.
        """
        self._description = value
        self._object_dict["description"] = value

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this model
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
    def relationships(self) -> list[ModelRelationshipObject]:
        """Getter for the relationships instance variable

        Returns:
            str: The relationships of this model
        """
        return self._relationships

    @relationships.setter
    def relationships(
        self,
        value,
    ):
        """Setter for the relationships instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of relationships is final; it cannot be altered."
        )

    @property
    def metrics(self) -> list[MetricReferenceObject]:
        """Getter for the metrics instance variable

        Returns:
            str: The metrics of this model
        """
        return self._metrics

    @metrics.setter
    def metrics(
        self,
        value,
    ):
        """Setter for the metrics instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of metrics is final; it cannot be altered."
        )

    @property
    def dimensions(self) -> list[str]:
        """Getter for the dimensions instance variable

        Returns:
            str: The dimensions of this model
        """
        return self._dimensions

    @dimensions.setter
    def dimensions(
        self,
        value,
    ):
        """Setter for the dimensions instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dimensions is final; it cannot be altered."
        )

    @property
    def aggregates(self) -> list[AggregateObject]:
        """Getter for the aggregates instance variable

        Returns:
            str: The aggregates of this model
        """
        return self._aggregates

    @aggregates.setter
    def aggregates(
        self,
        value,
    ):
        """Setter for the aggregates instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of aggregates is final; it cannot be altered."
        )

    @property
    def perspectives(self) -> list[PerspectiveObject]:
        """Getter for the perspectives instance variable

        Returns:
            str: The perspectives of this model
        """
        return self._perspectives

    @perspectives.setter
    def perspectives(
        self,
        value,
    ):
        """Setter for the perspectives instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of perspectives is final; it cannot be altered."
        )

    @property
    def drillthroughs(self) -> list[DrillthroughObject]:
        """Getter for the label instance variable

        Returns:
            str: The label of this model
        """
        return self._drillthroughs

    @drillthroughs.setter
    def drillthroughs(
        self,
        value,
    ):
        """Setter for the drillthroughs instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of drillthroughs is final; it cannot be altered."
        )

    @property
    def partitions(self) -> list[PartitionObject]:
        """Getter for the partitions instance variable

        Returns:
            str: The partitions of this model
        """
        return self._partitions

    @partitions.setter
    def partitions(
        self,
        value,
    ):
        """Setter for the partitions instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of partitions is final; it cannot be altered."
        )

    @property
    def overrides(self) -> OverridesObject:
        """Getter for the overrides instance variable

        Returns:
            str: The overrides of this model
        """
        return self._overrides

    @overrides.setter
    def overrides(
        self,
        value,
    ):
        """Setter for the overrides instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of overrides is final; it cannot be altered."
        )

    @property
    def dataset_properties(self) -> list[DatasetPropertiesObject]:
        """Getter for the dataset_properties instance variable

        Returns:
            str: The dataset_properties of this model
        """
        return self._dataset_properties

    @dataset_properties.setter
    def dataset_properties(
        self,
        value,
    ):
        """Setter for the dataset_properties instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset_properties is final; it cannot be altered."
        )

    @property
    def include_default_drillthrough(self) -> bool:
        """Getter for the include_default_drillthrough instance variable

        Returns:
            str: The include_default_drillthrough of this model
        """
        return self._include_default_drillthrough

    @include_default_drillthrough.setter
    def include_default_drillthrough(
        self,
        value,
    ):
        """Setter for the include_default_drillthrough instance variable. This variable is final, you must construct a new ModelObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of include_default_drillthrough is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "ModelObject":
        """

        Args:
            object_dict (Dict): the dictionary to unpack into a ModelObject
            file_path (str): the file location of the source

        Returns:
            ModelObject: a new model object
        """
        # `approved_dict` = required params + any optionals present in `object_dict`
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # parse relationships
        approved_dict["relationships"] = []
        for model_relationship in object_dict.get("relationships", []):
            approved_dict["relationships"].append(
                ModelRelationshipObject.parse_dict(
                    object_dict=model_relationship,
                    file_path=file_path,
                )
            )

        # parse metrics
        approved_dict["metrics"] = []
        for metric_ref in object_dict.get("metrics", []):
            approved_dict["metrics"].append(
                MetricReferenceObject.parse_dict(
                    object_dict=metric_ref,
                    file_path=file_path,
                )
            )

        # parse aggregates, if any
        if "aggregates" in object_dict:
            approved_dict["aggregates"] = []
            for aggregate in object_dict.get("aggregates", []):
                approved_dict["aggregates"].append(
                    AggregateObject.parse_dict(
                        object_dict=aggregate,
                        file_path=file_path,
                    )
                )

        # parse perspectives, if any
        if "perspectives" in object_dict:
            approved_dict["perspectives"] = []
            for perspective in object_dict.get("perspectives", []):
                approved_dict["perspectives"].append(
                    PerspectiveObject.parse_dict(
                        object_dict=perspective,
                        file_path=file_path,
                    )
                )

        # parse drillthroughs, if any
        if "drillthroughs" in object_dict:
            approved_dict["drillthroughs"] = []
            for drillthrough in object_dict.get("drillthroughs", []):
                approved_dict["drillthroughs"].append(
                    DrillthroughObject.parse_dict(
                        object_dict=drillthrough,
                        file_path=file_path,
                    )
                )

        # parse partitions, if any
        if "partitions" in object_dict:
            approved_dict["partitions"] = []
            for partition in object_dict.get("partitions", []):
                approved_dict["partitions"].append(
                    PartitionObject.parse_dict(
                        object_dict=partition,
                        file_path=file_path,
                    )
                )

        # parse overrides, if any
        if "overrides" in object_dict:
            approved_dict["overrides"] = OverridesObject.parse_dict(
                object_dict=object_dict.get("overrides"),
                file_path=file_path,
            )

        # parse dataset properties, if any
        if "dataset_properties" in object_dict:
            approved_dict["dataset_properties"] = []
            for dataset_property in object_dict.get("dataset_properties", []):
                approved_dict["dataset_properties"].append(
                    DatasetPropertiesObject.parse_dict(
                        object_dict=dataset_property,
                        file_path=file_path,
                    )
                )

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        # store `object_type`
        retObject._object_dict["object_type"] = SemanticObjectTypes.MODEL.value

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the model object back into a dictionary

        Returns:
            Dict: the output dictionary
        """
        ret_dict = deepcopy(self._object_dict)

        ret_dict["relationships"] = []
        for relationship in self._relationships:
            ret_dict["relationships"].append(relationship.to_export_dict())

        ret_dict["metrics"] = []
        for metric in self._metrics:
            ret_dict["metrics"].append(metric.to_export_dict())

        if self._aggregates is not None:
            ret_dict["aggregates"] = []
            for aggregate in self._aggregates:
                ret_dict["aggregates"].append(aggregate.to_export_dict())

        if self._perspectives is not None:
            ret_dict["perspectives"] = []
            for perspective in self._perspectives:
                ret_dict["perspectives"].append(perspective.to_export_dict())

        if self._drillthroughs is not None:
            ret_dict["drillthroughs"] = []
            for drillthrough in self._drillthroughs:
                ret_dict["drillthroughs"].append(drillthrough.to_export_dict())

        if self._partitions is not None:
            ret_dict["partitions"] = []
            for partition in self._partitions:
                ret_dict["partitions"].append(partition.to_export_dict())

        if self._overrides is not None:
            ret_dict["overrides"] = self._overrides.to_export_dict()

        if self._dataset_properties is not None:
            ret_dict["dataset_properties"] = []
            for dataset_property in self._dataset_properties:
                ret_dict["dataset_properties"].append(dataset_property.to_export_dict())

        return ret_dict
