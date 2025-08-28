from typing import List, Dict

from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.shared_degenerate_column_object import (
    SharedDegenerateColumnObject,
)
from atscale.base.private_enums import SemanticObjectTypes


class LevelAttributeObject(SemanticObject):

    _required_keys = [
        "unique_name",
        "label",
    ]
    _optional_keys = [
        "description",
        "is_hidden",
        "folder",
        "time_unit",
        "dataset",
        "name_column",
        "key_columns",
        "shared_degenerate_columns",
    ]

    # keys pertaining to level attribute data that only live in the `object_dict`
    # (i.e., that which aren't stored in properties)
    _misc_export_keys = [
        "is_unique_key",
        "contains_unique_keys",
        "exclude_from_dim_agg",
        "exclude_from_fact_agg",
        "sort_column",
        "allowed_calcs_for_dma",
    ]

    def __init__(
        self,
        unique_name: str,
        label: str,
        dataset: str = None,
        name_column: str = None,
        key_columns: List[str] = None,
        shared_degenerate_columns: List[SharedDegenerateColumnObject] = None,
        description: str = None,
        is_hidden: bool = None,
        folder: str = None,
        time_unit: str = None,
    ):
        """The class describing attributes associated with a particular dimension hierarchy

        Args:
            unique_name (str): The unique name of the level attribute
            label (str): The name of the level attribute
            dataset (str, optional): The source dataset that contains the columns that this level attribute is based on.
            Defaults to None.
            name_column (str, optional): The column whose values appear for this level in the consumption tool. Defaults
            to None.
            key_columns (List[str], optional): The dataset column that the level attribute is based on (all columns listed
            for compound keys). Defaults to None.
            shared_degenerate_columns (List[SharedDegenerateColumnObject], optional): The shared degenerate columns associated with
            this level attribute. Defaults to None.
            description (str, optional): The description of the level attribute. Defaults to None.
            is_hidden (bool, optional): Whether the level attribute is visible in the consumption tool. Defaults
            to None.
            folder (str, optional): The name of the folder in which this level attribute appears in the
            consumption tool. Defaults to None.
            time_unit (str, optional): The unit of time to use (for time dimensions only). Defaults to None.
        """
        # must either have
        #   – all of {`dataset`, `name_column`, `key_columns`} and no `shared_degenerate_columns`, or
        #   – `shared_degenerate_columns` and none of {`dataset`, `name_column`, `key_columns`},
        # and not both or neither
        if None not in [dataset, name_column, key_columns]:
            if shared_degenerate_columns is not None:
                raise atscale_errors.ValidationError(
                    "Must either pass all of {`dataset`, `name_column`, `key_columns`} or only `shared_degenerate_columns` to `LevelAttributeObject`, not all four."
                )

        elif [dataset, name_column, key_columns] != [None] * 3:
            raise atscale_errors.ValidationError(
                "Must pass {`dataset`, `name_column`, `key_columns`} all together to `LevelAttributeObject`."
            )

        # at this point, all of the inputs we're testing are None
        elif shared_degenerate_columns is None:
            raise atscale_errors.ValidationError(
                "Must either pass all of {`dataset`, `name_column`, `key_columns`} or only `shared_degenerate_columns` to `LevelAttributeObject`, not none of them."
            )

        self._object_type = SemanticObjectTypes.LEVEL_ATTRIBUTE
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._dataset = dataset
        self._name_column = name_column
        self._key_columns = key_columns
        self._description = description
        self._shared_degenerate_columns = shared_degenerate_columns
        self._is_hidden = is_hidden
        self._folder = folder
        self._time_unit = time_unit

        object_dict = {
            "unique_name": self._unique_name,
            "label": self._label,
        }
        if dataset is not None:
            object_dict["dataset"] = self._dataset
        if name_column is not None:
            object_dict["name_column"] = self._name_column
        if key_columns is not None:
            object_dict["key_columns"] = self._key_columns
        if shared_degenerate_columns is not None:
            object_dict["shared_degenerate_columns"] = self._shared_degenerate_columns
        if description is not None:
            object_dict["description"] = self._description
        if is_hidden is not None:
            object_dict["is_hidden"] = self._is_hidden
        if folder is not None:
            object_dict["folder"] = self._folder
        if time_unit is not None:
            object_dict["time_unit"] = self._time_unit

        self._object_dict = object_dict
        self._file_path = None

    @property
    def label(self) -> str:
        """Getter for the label instance variable

        Returns:
            str: The label of this level attribute
        """
        return self._label

    @label.setter
    def label(
        self,
        value,
    ):
        """Setter for the label instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of label is final; it cannot be altered."
        )

    @property
    def dataset(self) -> str:
        """Getter for the dataset instance variable

        Returns:
            str: The dataset of this level attribute
        """
        return self._dataset

    @dataset.setter
    def dataset(
        self,
        value,
    ):
        """Setter for the dataset instance variable. This variable is final, you must construct a new LevelAttribute.

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
        return self._name_column

    @name_column.setter
    def name_column(
        self,
        value,
    ):
        """Setter for the name_column instance variable. This variable is final, you must construct a new LevelAttribute.

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
            List[str]: The dataset column that the level attribute is based on (all columns listed for compound keys)
        """
        return self._key_columns

    @key_columns.setter
    def key_columns(
        self,
        value,
    ):
        """Setter for the key_columns instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of key_columns is final; it cannot be altered."
        )

    @property
    def shared_degenerate_columns(self) -> List[SharedDegenerateColumnObject]:
        """Getter for the shared_degenerate_columns instance variable

        Returns:
            List[str]: The shared degenerate columns for the level attribute object
        """
        return self._shared_degenerate_columns

    @shared_degenerate_columns.setter
    def shared_degenerate_columns(
        self,
        value,
    ):
        """Setter for the shared_degenerate_columns instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of shared_degenerate_columns is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of the level attribute
        """
        return self._description

    @description.setter
    def description(
        self,
        value,
    ):
        """Setter for the description instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of description is final; it cannot be altered."
        )

    @property
    def is_hidden(self) -> bool:
        """Getter for the is_hidden instance variable

        Returns:
            bool: Whether the level attribute is visible in consumption tools
        """
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(
        self,
        value,
    ):
        """Setter for the is_hidden instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of is_hidden is final; it cannot be altered."
        )

    @property
    def folder(self) -> str:
        """Getter for the folder instance variable

        Returns:
            str: The folder of the level attribute
        """
        return self._folder

    @folder.setter
    def folder(
        self,
        value,
    ):
        """Setter for the folder instance variable. This variable is final, you must construct a new LevelAttribute.

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
        return self._time_unit

    @time_unit.setter
    def time_unit(
        self,
        value,
    ):
        """Setter for the time_unit instance variable. This variable is final, you must construct a new LevelAttribute.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of time_unit is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "LevelAttributeObject":
        """
        Args:
            object_dict (Dict): the dictionary to unpack into a LevelAttributeObject
            file_path (str): the file location of the source

        Returns:
            LevelAttributeObject: a new level object
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

        # parse shared degenerate columns, if any
        if "shared_degenerate_columns" in object_dict:
            approved_dict["shared_degenerate_columns"] = []

            for shared_degenerate_column in object_dict.get("shared_degenerate_columns", []):
                approved_dict["shared_degenerate_columns"].append(
                    SharedDegenerateColumnObject.parse_dict(
                        shared_degenerate_column,
                        file_path,
                    )
                )

        # gather all level attribute data, whether stored on a property or otherwise
        all_level_attribute_data = {
            key: object_dict.get(key)
            for key in object_dict
            if key in cls._required_keys + cls._optional_keys + cls._misc_export_keys
            and object_dict.get(key) is not None
        }

        # update `object_dict` to reflect ALL level attribute data. this includes data which is only stored in `object_dict` and
        # not in LevelAttributeObject's properties.
        object_dict.update({key: all_level_attribute_data[key] for key in all_level_attribute_data})

        retObject = cls(**approved_dict)

        retObject._file_path = file_path
        retObject._object_dict = object_dict

        return retObject
