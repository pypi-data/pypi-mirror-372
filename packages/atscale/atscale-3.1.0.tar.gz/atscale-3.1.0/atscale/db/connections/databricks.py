from pandas import DataFrame
from cryptography.fernet import Fernet
from typing import Dict
import logging
import numpy as np
from inspect import getfullargspec

from atscale.errors import atscale_errors
from atscale.db.sql_connection import SQLConnection
from atscale.base import enums
from atscale.utils import validation_utils

logger = logging.getLogger(__name__)


class Databricks(SQLConnection):
    """The child class of SQLConnection whose implementation is meant to handle
    interactions with Databricks.
    """

    # NOTE: this was changed from "databrickssql" to "databricks" to reflect the
    #       return value of get_connected_warehouses. i don't believe this change
    #       breaks other tests, but noting it regardless

    platform_type_str: str = "databricks"

    conversion_dict = {
        "<class 'numpy.int32'>": "INT",
        "<class 'numpy.int64'>": "BIGINT",
        "<class 'numpy.uint64'>": "BIGINT",
        "<class 'numpy.float64'>": "DOUBLE",
        "<class 'str'>": "STRING",
        "<class 'numpy.bool_'>": "BOOLEAN",
        "<class 'numpy.bool'>": "BOOLEAN",
        "<class 'pandas._libs.tslibs.timestamps.Timestamp'>": "TIMESTAMP",
        "<class 'datetime.date'>": "DATE",
        "<class 'decimal.Decimal'>": "DECIMAL",
        "<class 'numpy.datetime64'>": "TIMESTAMP",
    }

    def __init__(
        self,
        host: str,
        catalog: str,
        schema: str,
        http_path: str,
        token: str = None,
        port: int = 443,
        warehouse_id: str = None,
    ):
        """Constructs an instance of the Databricks SQLConnection. Takes arguments necessary to find the host
            and schema. Since prompting login is not viable, this requires an authorization token.

        Args:
            host (str): The host of the intended Databricks connections
            catalog (str): The catalog of the intended Databricks connections
            schema (str): The schema of the intended Databricks connections
            http_path (str): The web path of the intended Databricks connections
            token (str, optional): The authorization token needed to interact with Databricks. Will prompt if None
            port (int, optional): A port for the connection. Defaults to 443.
            warehouse_id (str, optional): The AtScale warehouse id to automatically associate the connection with if writing tables. Defaults to None.
        """

        try:
            from databricks import sql
        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("databricks", str(e))

        super().__init__(warehouse_id)

        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())
        self.__fernet = Fernet(Fernet.generate_key())

        if token:
            self._token = self.__fernet.encrypt(token.encode())
        else:
            self._token = None
        self._host = host
        self._catalog = catalog
        self._schema = schema
        self._http_path = http_path
        self._port = port
        try:
            validation_connection = sql.connect(
                server_hostname=self._host,
                http_path=self._http_path,
                access_token=self.__fernet.decrypt(self._token).decode(),
            )
            validation_connection.close()
        except:
            logger.error("Unable to create database connection, please verify the inputs")
            raise

    @property
    def token(self) -> str:
        raise atscale_errors.UnsupportedOperationException("Token cannot be retrieved.")

    @token.setter
    def token(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._token = self.__fernet.encrypt(value.encode())

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._host = value

    @property
    def catalog(self) -> str:
        return self._catalog

    @catalog.setter
    def catalog(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._catalog = value

    @property
    def schema(self) -> str:
        return self._schema

    @schema.setter
    def schema(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._schema = value

    @property
    def http_path(self) -> str:
        return self._http_path

    @http_path.setter
    def http_path(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._http_path = value

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(
        self,
        value,
    ):
        # validate the non-null inputs
        if value is None:
            raise ValueError(f"The following required parameters are None: value")
        self._port = value

    @property
    def _database(self):
        return self._catalog

    def clear_auth(self):
        """Clears any authentication information, like password or token from the connection."""
        self._token = None

    @staticmethod
    def _format_types(
        dataframe: DataFrame,
    ) -> Dict:
        types = {}
        for i in dataframe.columns:
            if (
                str(type(dataframe[i].loc[~dataframe[i].isnull()].iloc[0]))
                in Databricks.conversion_dict
            ):
                types[i] = Databricks.conversion_dict[
                    str(type(dataframe[i].loc[~dataframe[i].isnull()].iloc[0]))
                ]
            else:
                types[i] = Databricks.conversion_dict["<class 'str'>"]
        return types

    def submit_queries(
        self,
        query_list: list,
    ) -> list:
        inspection = getfullargspec(self.submit_queries)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        from databricks import sql

        connection = sql.connect(
            server_hostname=self._host,
            http_path=self._http_path,
            access_token=self.__fernet.decrypt(self._token).decode(),
        )
        cursor = connection.cursor()

        results = []
        for query in query_list:
            cursor.execute(query)
            result = cursor.fetchall_arrow()
            df = result.to_pandas()
            results.append(df)
        cursor.close()
        connection.close()
        return results

    def execute_statements(
        self,
        statement_list: list,
    ):
        inspection = getfullargspec(self.execute_statements)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        # same implementation is in Synapse, so if you need to change one please change the other
        from databricks import sql

        connection = sql.connect(
            server_hostname=self._host,
            http_path=self._http_path,
            access_token=self.__fernet.decrypt(self._token).decode(),
        )
        cursor = connection.cursor()
        for statement in statement_list:
            cursor.execute(statement)

    def _create_table(
        self,
        table_name: str,
        types: Dict,
        cursor,
    ):
        # If the table exists we'll just let this fail and raise the appropriate exception.
        # Related checking to handle gracefully is within calling methods.
        operation = f"CREATE TABLE {self._create_table_path(table_name)} ("
        for key, value in types.items():
            operation += f"`{key}` {value}, "
        operation = operation[:-2]
        operation += ")"
        cursor.execute(operation)
        # autocommit should be on by default

    def write_df_to_db(
        self,
        table_name: str,
        dataframe: DataFrame,
        if_exists: enums.TableExistsAction = enums.TableExistsAction.ERROR,
        chunksize: int = 1000,
    ):
        inspection = getfullargspec(self.write_df_to_db)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if if_exists == enums.TableExistsAction.IGNORE:
            raise ValueError(
                "IGNORE action type is not supported for this operation, please adjust if_exists parameter"
            )

        from databricks import sql

        connection = sql.connect(
            server_hostname=self._host,
            http_path=self._http_path,
            access_token=self.__fernet.decrypt(self._token).decode(),
        )
        cursor = connection.cursor()

        tables = cursor.tables(
            table_name=table_name, schema_name=self.schema, catalog_name=self.catalog
        ).fetchall()
        cursor.execute(f"USE CATALOG {self.catalog}")
        if len(tables) > 1:
            raise atscale_errors.CollisionError(
                f"{table_name} already exists in schema: {self.schema} for catalog: "
                f"{self.catalog} with type {tables[0].asDict().get('TABLE_TYPE')} "
                f"and must be dropped to create a table with the same name"
            )
        if len(tables) == 1:
            cursor.execute(f"show tables in {self.catalog}.{self.schema}")
            existing_tables = cursor.fetchall_arrow().to_pandas()["tableName"].values
            cursor.execute(f"show views in {self.catalog}.{self.schema}")
            existing_views = cursor.fetchall_arrow().to_pandas()["viewName"].values
            only_existing_tables = np.setdiff1d(existing_tables, existing_views)
            if table_name not in only_existing_tables:
                raise atscale_errors.CollisionError(
                    f"Object with name {table_name} already exists in schema: {self.schema} for catalog: "
                    f"{self.catalog} and must be dropped to create a table with the same name"
                )
            exists = True
        else:
            exists = False

        if exists and if_exists == enums.TableExistsAction.ERROR:
            raise atscale_errors.CollisionError(
                f"A table or view named: {table_name} already exists in schema: {self.schema} for catalog: {self.catalog}"
            )

        types = self._format_types(dataframe)

        if exists and if_exists == enums.TableExistsAction.OVERWRITE:
            operation = f"DROP TABLE {self._create_table_path(table_name)}"
            cursor.execute(operation)
            self._create_table(table_name, types, cursor)
        elif not exists:
            self._create_table(table_name, types, cursor)

        # add in break characters
        for key, value in types.items():
            if "STRING" in value:
                dataframe[key] = dataframe[key].str.replace(r"'", r"\'")

        operation = f"INSERT INTO {self._create_table_path(table_name)} VALUES ("

        list_df = [dataframe[i : i + chunksize] for i in range(0, dataframe.shape[0], chunksize)]
        for df in list_df:
            op_copy = operation
            for index, row in df.iterrows():
                for col in df.columns:
                    if "STRING" in types[col] or "DATE" in types[col] or "TIMESTAMP" in types[col]:
                        op_copy += f"'{row[col]}', "
                    else:
                        op_copy += f"{row[col]}, ".replace("nan", "null")
                op_copy = op_copy[:-2]
                op_copy += "), ("
            op_copy = op_copy[:-3]
            cursor.execute(op_copy)
        # adding close of cursor which I didn't see before
        cursor.close()
        connection.close()

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
        return f"{self._column_quote()}{self.catalog}{self._column_quote()}.{self._column_quote()}{self.schema}{self._column_quote()}.{self._column_quote()}{table_name}{self._column_quote()}"
