from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from pandas import DataFrame
from inspect import getfullargspec
from copy import deepcopy

from atscale.utils import validation_utils
from atscale.base import enums
from atscale.errors import atscale_errors
from atscale.utils.db_utils import _WarehouseInfo


class SQLConnection(ABC):
    """The abstract class meant to standardize functionality related to various DB systems that AI-Link supports.
    This includes submitting queries, writeback, and engine disposal.
    """

    def __init__(self, warehouse_id: str = None):
        """Constructs an instance of the SQLAlchemyConnection SQLConnection

        Args:
            warehouse_id (str, optional): The AtScale warehouse id to automatically associate the connection with if writing tables. Defaults to None.
        """
        self._warehouse_id = warehouse_id

    @property
    def warehouse_id(self) -> str:
        return self._warehouse_id

    @warehouse_id.setter
    def warehouse_id(self, value):
        self._warehouse_id = value

    platform_type_str: str
    """The string representation of the platform type, matches with atscale"""

    @property
    def platform_type_str(self) -> str:
        """Getter for a string representation of the instance type of this SQLConnection

        Returns:
            str:
        """
        return SQLConnection.platform_type_str

    @platform_type_str.setter
    def platform_type_str(
        self,
        value,
    ):
        """Setter for the platform_type_str instance variable. This variable is final, please construct a new SQLConnection.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The platform type string of a SQLConnection class is final; it cannot be altered."
        )

    @abstractmethod
    def clear_auth(self):
        """Clears any authentication information, like password or token from the connection."""
        raise NotImplementedError

    def submit_query(
        self,
        query: str,
    ) -> DataFrame:
        """This submits a single query and reads the results into a DataFrame. It closes the connection after each query.

        Args:
            query (str): SQL statement to be executed

        Returns:
            DataFrame: the results of executing the SQL statement or query parameter, read into a DataFrame
        """
        inspection = getfullargspec(self.submit_query)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        return self.submit_queries([query])[0]

    @abstractmethod
    def submit_queries(
        self,
        query_list: list,
    ) -> List:
        """Submits a list of queries, collecting the results in a list of dictionaries.

        Args:
            query_list (list): a list of queries to submit.

        Returns:
            List(DataFrame): A list of pandas DataFrames containing the results of the queries.
        """
        raise NotImplementedError

    def execute_statement(
        self,
        statement: str,
    ):
        """This executes a single SQL statements. Does not return any results but may trigger an exception.

        Args:
            statement (str): SQL statement to be executed
        """
        inspection = getfullargspec(self.execute_statement)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        self.execute_statements([statement])

    @abstractmethod
    def execute_statements(
        self,
        statements_list: list,
    ):
        """Executes a list of SQL statements. Does not return any results but may trigger an exception.

        Args:
            statements_list (list): a list of SQL statements to execute.
        """
        raise NotImplementedError

    def _fix_table_name(
        self,
        table_name: str,
    ):
        return table_name

    def _fix_column_name(
        self,
        column_name: str,
    ):
        return column_name

    @abstractmethod
    def write_df_to_db(
        self,
        table_name: str,
        dataframe: DataFrame,
        dtypes: Dict = None,
        if_exists: enums.TableExistsAction = enums.TableExistsAction.ERROR,
        chunksize: int = 1000,
    ):
        """Writes the provided pandas DataFrame into the provided table name. Can pass in if_exists to indicate the intended behavior if
            the provided table name is already taken.

        Args:
            table_name (str): What table to write the dataframe into
            dataframe (DataFrame): The pandas DataFrame to write into the table
            dtypes (Dict, optional): the datatypes of the passed dataframe. Keys should match the column names. Defaults to None
                and type will be text.
            if_exists (enums.TableExistsAction, optional): The intended behavior in case of table name collisions.
                Defaults to enums.TableExistsAction.ERROR.
            chunksize (int, optional): the chunksize for the write operation.
        """
        raise NotImplementedError

    def _write_pysparkdf_to_external_db(
        self,
        pyspark_dataframe,
        jdbc_format: str,
        jdbc_options: Dict[str, str],
        table_name: str = None,
        if_exists: enums.TableExistsAction = enums.TableExistsAction.ERROR,
    ):
        """Writes the provided pyspark DataFrame into the provided table name via jdbc. Can pass in if_exists to indicate the intended behavior if
            the provided table name is already taken.

        Args:
            pyspark_dataframe (pyspark.sql.dataframe.DataFrame): The pyspark dataframe to write
            jdbc_format (str): the driver class name. For example: 'jdbc', 'net.snowflake.spark.snowflake', 'com.databricks.spark.redshift'
            jdbc_options (Dict[str,str]): Case-insensitive to specify connection options for jdbc
            table_name (str): What table to write the dataframe into, can be none if 'dbtable' option specified
            if_exists (enums.TableExistsAction, optional): The intended behavior in case of table name collisions.
                Defaults to enums.TableExistsAction.ERROR.
        """
        try:
            from pyspark.sql import SparkSession
        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("spark", str(e))

        # we want to avoid editing the source dictionary
        jdbc_copy = deepcopy(jdbc_options)

        # quick check on passed tablename parameters
        if jdbc_copy.get("dbtable") is None:
            if table_name is None:
                raise ValueError(
                    "A table name must be specified for the written table. This can be done "
                    'either through the jdbc_options key "dbtable" or the table_name function parameter'
                )
            else:
                jdbc_copy["dbtable"] = table_name
        elif table_name is not None:
            if table_name != jdbc_copy.get("dbtable"):
                raise ValueError(
                    'Different table names passed via the jdbc_options key "dbtable" '
                    "and the table_name function parameter. Please get one of the 2 options"
                )

        pyspark_dataframe.write.format(jdbc_format).options(**jdbc_copy).mode(
            if_exists.value
        ).save()

    def _verify(
        self,
        con: _WarehouseInfo,
    ) -> bool:
        if con is None:
            return False

        return self.platform_type_str == con.get("platform")

    def _create_table_path(
        self,
        table_name: str,
    ) -> str:
        """generates a full table file path using instance variables.

        Args:
            table_name (str): the table name to append

        Returns:
            str: the queriable location of the table
        """
        return table_name

    def _generate_date_table(self):
        df_date = pd.DataFrame()
        df_date["date"] = pd.date_range("1/1/1900", "12/31/2099")
        df_date["year"] = df_date["date"].dt.year
        df_date["month"] = df_date["date"].dt.month
        df_date["month_name"] = df_date["date"].dt.month_name()
        df_date["day_name"] = df_date["date"].dt.day_name()
        df_date["date"] = df_date["date"].dt.date
        self.write_df_to_db("atscale_date_table", df_date)

    @staticmethod
    def _column_quote():
        return "`"
