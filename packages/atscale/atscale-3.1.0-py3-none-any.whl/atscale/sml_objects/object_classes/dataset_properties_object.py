from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.base.private_enums import SemanticObjectTypes


class DatasetPropertiesObject(SemanticObject):
    _required_keys = [
        "dataset_unique_name",
    ]
    _optional_keys = [
        "allow_aggregates",
        "allow_local_aggs",
        "allow_peer_aggs",
        "allow_preferred_aggs",
        "create_hinted_aggregate",
    ]

    def __init__(
        self,
        dataset_unique_name: str,
        allow_aggregates: bool = None,
        allow_local_aggs: bool = None,
        allow_peer_aggs: bool = None,
        allow_preferred_aggs: bool = None,
        create_hinted_aggregate: bool = None,
    ):
        """Dataset properties to use within the repository.

        Args:
            dataset_unique_name (str): The unique name of the dataset whose properties are described by this object.
            allow_aggregates (bool, optional): Whether the query engine can create aggregates for datasets in the repository. Defaults to None.
            allow_local_aggs (bool, optional): Whether local aggregation is enabled for datasets in the repository. Defaults to None.
            allow_peer_aggs (bool, optional): Whether aggregation on data derived from datasets in data warehouses that are different from the source dataset is enabled. Defaults to None.
            allow_preferred_aggs (bool, optional): Whether to allow preffered aggs from the dataset. Defaults to None.
            create_hinted_aggregate (bool, optional): Whether to create a hinted agg from a qds dataset. Defaults to None.
        """

        self._object_type = SemanticObjectTypes.DATASET_PROPERTIES
        self._dataset_unique_name = dataset_unique_name

        param_check_list = [
            allow_aggregates,
            allow_local_aggs,
            allow_peer_aggs,
            allow_preferred_aggs,
            create_hinted_aggregate,
        ]
        if all(x is None for x in param_check_list):
            raise atscale_errors.ValidationError(
                "Invalid DatasetPropertiesObject; at least 1 of the optional aggregate parameters must not be None"
            )

        self._allow_aggregates = allow_aggregates
        self._allow_local_aggs = allow_local_aggs
        self._allow_peer_aggs = allow_peer_aggs
        self._allow_preferred_aggs = allow_preferred_aggs
        self._create_hinted_aggregate = create_hinted_aggregate

        object_dict = {
            "dataset_unique_name": dataset_unique_name,
        }
        if allow_aggregates is not None:
            object_dict["allow_aggregates"] = self._allow_aggregates
        if allow_local_aggs is not None:
            object_dict["allow_local_aggs"] = self._allow_local_aggs
        if allow_peer_aggs is not None:
            object_dict["allow_peer_aggs"] = self._allow_peer_aggs
        if allow_preferred_aggs is not None:
            object_dict["allow_preferred_aggs"] = self._allow_preferred_aggs
        if create_hinted_aggregate is not None:
            object_dict["create_hinted_aggregate"] = self._create_hinted_aggregate

        self._object_dict = object_dict

    @property
    def dataset_unique_name(self) -> str:
        """Getter for the dataset_unique_name instance variable

        Returns:
            str: The unique name of the dataset whose properties are described by this object.
        """
        return self._dataset_unique_name

    @dataset_unique_name.setter
    def dataset_unique_name(
        self,
        value,
    ):
        """Setter for the dataset_unique_name instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dataset_unique_name is final; it cannot be altered."
        )

    @property
    def allow_aggregates(self) -> bool:
        """Getter for the allow_aggregates instance variable

        Returns:
            bool: Whether the query engine can create aggregates for datasets in the repository.
        """
        return self._allow_aggregates

    @allow_aggregates.setter
    def allow_aggregates(
        self,
        value,
    ):
        """Setter for the allow_aggregates instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of allow_aggregates is final; it cannot be altered."
        )

    @property
    def allow_local_aggs(self) -> bool:
        """Getter for the allow_local_aggs instance variable

        Returns:
            bool: Whether local aggregation is enabled for datasets in the repository.
        """
        return self._allow_local_aggs

    @allow_local_aggs.setter
    def allow_local_aggs(
        self,
        value,
    ):
        """Setter for the allow_local_aggs instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of allow_local_aggs is final; it cannot be altered."
        )

    @property
    def allow_peer_aggs(self) -> bool:
        """Getter for the allow_peer_aggs instance variable

        Returns:
            bool: Whether aggregation on data derived from datasets in data warehouses that are different from the source dataset is enabled.
        """
        return self._allow_peer_aggs

    @allow_peer_aggs.setter
    def allow_peer_aggs(
        self,
        value,
    ):
        """Setter for the allow_peer_aggs instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of allow_peer_aggs is final; it cannot be altered."
        )

    @property
    def allow_preferred_aggs(self) -> bool:
        """Getter for the allow_preferred_aggs instance variable

        Returns:
            bool: Whether to allowed preffered aggregates from the dataset.
        """
        return self._allow_preferred_aggs

    @allow_preferred_aggs.setter
    def allow_preferred_aggs(
        self,
        value,
    ):
        """Setter for the allow_preferred_aggs instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of allow_preferred_aggs is final; it cannot be altered."
        )

    @property
    def create_hinted_aggregate(self) -> bool:
        """Getter for the create_hinted_aggregate instance variable

        Returns:
            bool: Whether to allow creation of a hinted agg from a qds dataset.
        """
        return self._create_hinted_aggregate

    @create_hinted_aggregate.setter
    def create_hinted_aggregate(
        self,
        value,
    ):
        """Setter for the create_hinted_aggregate instance variable. This variable is final, you must construct a new DatasetPropertiesObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of create_hinted_aggregate is final; it cannot be altered."
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
