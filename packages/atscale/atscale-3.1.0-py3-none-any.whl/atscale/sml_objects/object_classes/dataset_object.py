from typing import Dict
from copy import deepcopy
from atscale.errors import atscale_errors
from atscale.sml_objects.yaml_object import YamlObject
from atscale.sml_objects.object_classes.alternate_object import AlternateObject
from atscale.sml_objects.object_classes.column_object import ColumnObject
from atscale.sml_objects.object_classes.dialect_object import DialectObject
from atscale.sml_objects.object_classes.incremental_object import IncrementalObject
from atscale.base.private_enums import SemanticObjectTypes


class DatasetObject(YamlObject):
    _required_keys = [
        "unique_name",
        "connection_id",
        "label",
        "columns",
    ]
    _optional_keys = [
        "sql",
        "table",
        "description",
        "dialects",
        "incremental",
        "immutable",
        "alternate",
    ]

    def __init__(
        self,
        unique_name: str,
        connection_id: str,
        columns: list[ColumnObject],
        label: str = None,
        description: str = None,
        sql: str = None,
        table: str = None,
        dialects: list[DialectObject] = None,
        incremental: IncrementalObject = None,
        immutable: bool = None,
        alternate: AlternateObject = None,
    ):
        """Represents a dataset

        Args:
            unique_name (str): The name of the dataset.
            connection_id (str): The AtScale connection to associate with this dataset.
            columns (list): The columns in the dataset.
            label (str, optional): The user facing name of the dataset. Defaults to None to use the unique_name.
            description (str, optional): The description of the dataset. Defaults to None to leave blank.
            sql (str): The sql for this dataset if it is a qds. Defaults to None for a table.
            table (str): The table for this dataset. Defaults to None for a qds.
            dialects (list[DialectObject], optional): The alternate sql for different dialects. Defaults to None.
            incremental (IncrementalObject, optional): The incremental build information for this dataset. Defaults to None.
            immutable (bool, optional): Whether the dataset is immutable. Defaults to None.
            alternate (AlternateObject, optional): The alternate options for this dataset. Defaults to None.
        """
        if table is None and sql is None:
            raise atscale_errors.ValidationError("table or sql must be provided")

        if table is not None and sql is not None:
            raise atscale_errors.ValidationError("only one of table or sql can be provided")

        self._object_type = SemanticObjectTypes.DATASET
        self._unique_name = unique_name

        if not label:
            label = unique_name
        self._label = label

        self._connection_id = connection_id
        self._columns = columns
        self._sql = sql
        self._table = table
        self._dialects = dialects
        self._description = description
        self._incremental = incremental
        self._immutable = immutable
        self._alternate = alternate

        self._object_dict = {
            "unique_name": self._unique_name,
            "connection_id": self._connection_id,
            "columns": self._columns,
            "object_type": self._object_type.value,
            "label": self._label,
        }

        if self._description is not None:
            self._object_dict["description"] = self._description
        if self._sql is not None:
            self._object_dict["sql"] = self._sql
        if self._table is not None:
            self._object_dict["table"] = self._table
        if self._dialects is not None:
            self._object_dict["dialects"] = self._dialects
        if self._incremental is not None:
            self._object_dict["incremental"] = self._incremental
        if self._immutable is not None:
            self._object_dict["immutable"] = self._immutable
        if self._alternate is not None:
            self._object_dict["alternate"] = self._alternate

        self._file_path = None

    @property
    def connection_id(self) -> str:
        """Getter for the connection_id instance variable

        Returns:
            str: The connection_id of this dataset
        """
        return self._connection_id

    @connection_id.setter
    def connection_id(
        self,
        value,
    ):
        """Setter for the connection_id instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of connection_id is final; it cannot be altered."
        )

    @property
    def table(self) -> str:
        """Getter for the table instance variable

        Returns:
            str: The table of this dataset
        """
        return self._table

    @table.setter
    def table(
        self,
        value,
    ):
        """Setter for the table instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of table is final; it cannot be altered."
        )

    @property
    def sql(self) -> str:
        """Getter for the sql instance variable

        Returns:
            str: The sql of this dataset
        """
        return self._sql

    @sql.setter
    def sql(
        self,
        value,
    ):
        """Setter for the sql instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of sql is final; it cannot be altered."
        )

    @property
    def columns(self) -> list[ColumnObject]:
        """Getter for the columns instance variable

        Returns:
            str: The columns of this dataset
        """
        return self._columns

    @columns.setter
    def columns(
        self,
        value,
    ):
        """Setter for the columns instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of columns is final; it cannot be altered."
        )

    @property
    def alternate(self) -> AlternateObject:
        """Getter for the alternate instance variable

        Returns:
            str: The alternate of this dataset
        """
        return self._alternate

    @alternate.setter
    def alternate(
        self,
        value,
    ):
        """Setter for the alternate instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of alternate is final; it cannot be altered."
        )

    @property
    def immutable(self) -> bool:
        """Getter for the immutable instance variable

        Returns:
            str: The immutable of this dataset
        """
        return self._immutable

    @immutable.setter
    def immutable(
        self,
        value,
    ):
        """Setter for the immutable instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of immutable is final; it cannot be altered."
        )

    @property
    def incremental(self) -> IncrementalObject:
        """Getter for the incremental instance variable

        Returns:
            str: The incremental of this dataset
        """
        return self._incremental

    @incremental.setter
    def incremental(
        self,
        value,
    ):
        """Setter for the incremental instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of incremental is final; it cannot be altered."
        )

    @property
    def dialects(self) -> list[DialectObject]:
        """Getter for the dialects instance variable

        Returns:
            str: The dialects of this dataset
        """
        return self._dialects

    @dialects.setter
    def dialects(
        self,
        value,
    ):
        """Setter for the dialects instance variable. This variable is final, you must construct a new DatasetObject.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of dialects is final; it cannot be altered."
        )

    @property
    def description(self) -> str:
        """Getter for the description instance variable

        Returns:
            str: The description of this dataset
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

    @classmethod
    def parse_dict(
        cls,
        object_dict: Dict,
        file_path: str,
    ) -> "DatasetObject":
        """

        Args:
            object_dict (Dict): the dictionary to unpack into a DatasetObject
            file_path (str): the file location of the source

        Returns:
            DatasetObject: a new dataset object
        """
        # `approved_dict` = required params + any optionals present in `object_dict`
        approved_dict = cls._get_required(
            inbound_dict=object_dict,
            req_keys=cls._required_keys,
            file_path=file_path,
        ) | {key: object_dict[key] for key in cls._optional_keys if key in object_dict}

        # convert semantic objects in approved dict to Pythonic representations
        ## parse columns
        if "columns" in object_dict:
            approved_dict["columns"] = []

            for column in object_dict.get("columns", []):
                approved_dict["columns"].append(
                    ColumnObject.parse_dict(
                        object_dict=column,
                        file_path=file_path,
                    )
                )

        ## parse dialects, if any
        if "dialects" in object_dict:
            approved_dict["dialects"] = []

            for dialect in object_dict.get("dialects", []):
                approved_dict["dialects"].append(
                    DialectObject.parse_dict(
                        object_dict=dialect,
                        file_path=file_path,
                    )
                )

        ## parse incremental, if any
        if "incremental" in object_dict:
            approved_dict["incremental"] = IncrementalObject.parse_dict(
                object_dict=object_dict.get("incremental"),
                file_path="",
            )

        ## parse alternate, if any
        if "alternate" in object_dict:
            approved_dict["alternate"] = AlternateObject.parse_dict(
                object_dict=object_dict.get("alternate"),
                file_path="",
            )

        # construct object
        retObject = cls(**approved_dict)
        retObject._file_path = file_path

        # store any irrelevant parameters that may have been passed in `object_dict` in addition
        # to the Pythonic semantic object representations
        retObject._object_dict = object_dict | approved_dict

        # store `object_type`
        retObject._object_dict["object_type"] = SemanticObjectTypes.DATASET.value

        return retObject

    def to_export_dict(self) -> Dict:
        """Packs the values of the dataset object back into a dictionary

        Returns:
            Dict: the output dictionary
        """
        ret_dict = deepcopy(self._object_dict)

        ret_dict["columns"] = []
        for column in self._columns:
            ret_dict["columns"].append(column.to_export_dict())

        if self._dialects is not None:
            ret_dict["dialects"] = []
            for dialect in self._dialects:
                ret_dict["dialects"].append(dialect.to_export_dict())

        if self._incremental is not None:
            ret_dict["incremental"] = self._incremental.to_export_dict()

        if self._alternate is not None:
            ret_dict["alternate"] = self._alternate.to_export_dict()

        return ret_dict
