from typing import Dict
from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.semantic_object import SemanticObject
from atscale.sml_objects.object_classes.dialect_object import DialectObject
from atscale.sml_objects.object_classes.map_object import MapObject
from atscale.base.private_enums import SemanticObjectTypes


class ColumnObject(SemanticObject):
    _required_keys = ["name"]
    _optional_keys = ["data_type", "sql", "parent_column"]

    def __init__(
        self,
        name: str,
        data_type: str = None,
        sql: str = None,
        dialects: list[DialectObject] = None,
        map: MapObject = None,
        parent_column: str = None,
    ):
        """Represents an aggregation method over a numeric column

        Args:
            name (str): the name of the column
            data_type (str, optional): The column's data type if it is not a mapping. Defaults to None.
            sql (str, optional): The sql if it is a calculated column. Defaults to None.
            dialects (list[DialectObject], optional): Alternative sql for different dialects if it is a calculated column. Defaults to None.
            map (MapObject, optional): The mapping metadata if it is a column mapping. Defaults to None.
            parent_column (str, optional): The parent mapping if this is a mapped column. Defaults to None.
        """
        if map is None and data_type is None:
            raise atscale_errors.ValidationError(
                "data_type must be provided for columns that are not mappings"
            )

        if map is not None and (
            dialects is not None
            or sql is not None
            or data_type is not None
            or parent_column is not None
        ):
            raise atscale_errors.ValidationError("map should only be provided with name")

        if sql is not None and (map is not None or parent_column is not None):
            raise atscale_errors.ValidationError(
                "sql should only be provided with name, data_type, and optionally dialect"
            )

        if parent_column is not None and (
            dialects is not None or sql is not None or map is not None
        ):
            raise atscale_errors.ValidationError(
                "parent column should only be provided with name and data_type"
            )

        if dialects is not None and sql is None:
            raise atscale_errors.ValidationError("dialects should only be provided along with sql")

        self._object_type = SemanticObjectTypes.COLUMN
        self._name = name
        self._data_type = data_type
        self._dialects = dialects
        self._map = map
        self._parent_column = parent_column
        self._sql = sql

        self._object_dict = {
            "name": self._name,
        }

        if self._parent_column is not None:
            self._object_dict["parent_column"] = self._parent_column

        if self._sql is not None:
            self._object_dict["sql"] = self._sql

        if self._data_type is not None:
            self._object_dict["data_type"] = self._data_type

    @property
    def name(self) -> str:
        """Getter for the name instance variable

        Returns:
            str: The name of this column
        """
        return self._name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def parent_column(self) -> str:
        """Getter for the parent_column instance variable

        Returns:
            str: The parent_column of this column
        """
        return self._parent_column

    @parent_column.setter
    def parent_column(
        self,
        value,
    ):
        """Setter for the parent_column instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of parent_column is final; it cannot be altered."
        )

    @property
    def map(self) -> MapObject:
        """Getter for the map instance variable

        Returns:
            str: The map of this column
        """
        return self._map

    @map.setter
    def map(
        self,
        value,
    ):
        """Setter for the map instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of map is final; it cannot be altered."
        )

    @property
    def dialects(self) -> list[DialectObject]:
        """Getter for the dialects instance variable

        Returns:
            str: The dialects of this column
        """
        return self._dialects

    @dialects.setter
    def dialects(
        self,
        value,
    ):
        """Setter for the dialects instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dialects is final; it cannot be altered."
        )

    @property
    def sql(self) -> str:
        """Getter for the sql instance variable

        Returns:
            str: The sql of this column
        """
        return self._sql

    @sql.setter
    def sql(
        self,
        value,
    ):
        """Setter for the sql instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter sql be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sql is final; it cannot be altered."
        )

    @property
    def data_type(self) -> str:
        """Getter for the data_type instance variable

        Returns:
            str: The data_type of this column
        """
        return self._data_type

    @data_type.setter
    def data_type(
        self,
        value,
    ):
        """Setter for the data_type instance variable. This variable is final, you must construct a new ColumnObject.

        Args:
            value: setter data_type be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of data_type is final; it cannot be altered."
        )

    @classmethod
    def parse_dict(
        cls,
        object_dict=Dict,
        file_path=str,
    ) -> "ColumnObject":
        """

        Args:
            object_dict (Dict): the dictionary to unpack into a ColumnObject
            file_path (str): the file location of the source

        Returns:
            ColumnObject: a new column object
        """
        approved_dict = cls._get_required(
            inbound_dict=object_dict, req_keys=cls._required_keys, file_path=file_path
        )

        optionals_existing = {
            key: object_dict[key] for key in cls._optional_keys if key in object_dict
        }

        approved_dict.update(optionals_existing)

        if "dialects" in object_dict and object_dict.get("dialects") is not None:
            approved_dict["dialects"] = []
            for dialect in object_dict.get("dialects", []):
                approved_dict["dialects"].append(DialectObject.parse_dict(dialect, file_path))

        if "map" in object_dict and object_dict.get("map") is not None:
            approved_dict["map"] = MapObject.parse_dict(object_dict["map"], file_path)

        retObject = cls(**approved_dict)

        retObject._object_dict = object_dict

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the column object back into a dictionary

        Returns:
            Dict: the output dictionary
        """

        ret_dict = deepcopy(self._object_dict)
        if self._dialects is not None:
            ret_dict["dialects"] = []
            for dialect in self._dialects:
                ret_dict["dialects"].append(dialect.to_export_dict())
        if self._map is not None:
            ret_dict["map"] = self._map.to_export_dict()
        return ret_dict

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
