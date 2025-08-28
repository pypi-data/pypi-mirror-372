import logging
from inspect import getfullargspec
import warnings
import pandas as pd
from pandas import read_sql_query

from typing import List, Dict, Tuple, Any

from atscale.errors import atscale_errors
from atscale.db.sql_connection import SQLConnection

from atscale.catalog.catalog import Catalog
from atscale.data_model.dm_helpers import (
    dmv_helpers,
    metadata_helpers,
    model_validation_helpers,
    query_gen_helpers,
)
from atscale.utils import request_utils
from atscale.utils import validation_utils
from atscale.base import endpoints, enums, private_enums

logger = logging.getLogger(__name__)


class DataModel:
    """Creates an object corresponding to an AtScale Data Model. Takes an existing model id and
    AtScale Catalog object to construct an object that deals with functionality related to model
    datasets and columns, as well as reading data.
    """

    def __init__(
        self,
        catalog: Catalog,
        data_model_id: str,
    ):
        """A Data Model is an abstraction that represents a perspective or cube within AtScale.

        Args:
            catalog (Catalog): the AtScale Catalog object the model is a part of
            data_model_id (str): the unique identifier of the model in question
        """
        inspection = getfullargspec(self.__init__)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        self.__id = data_model_id
        self.__catalog = catalog
        url = endpoints._endpoint_catalog(self.__catalog.repo._atconn, catalog_id=self.__catalog.id)
        response = self.__catalog.repo._atconn._submit_request(
            request_type=private_enums.RequestType.GET, url=url
        )
        model_dict = {}
        for model in response.json().get("models", []):
            if model.get("id") == self.__id:
                model_dict = model
                break
        if model_dict == {}:
            raise atscale_errors.ObjectNotFoundError(
                f"Unable to find data model with id: {data_model_id} in catalog: {catalog}"
            )
        self.__name = model_dict.get("name")
        self.__caption = model_dict.get("caption")
        self.__is_perspective = model_dict.get("type") == "perspective"

    @property
    def id(self) -> str:
        """Getter for the id instance variable

        Returns:
            str: The id of this model
        """
        return self.__id

    @id.setter
    def id(
        self,
        value,
    ):
        """Setter for the id instance variable. This variable is final, please construct a new DataModel.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of id is final; it cannot be altered."
        )

    @property
    def name(self) -> str:
        """Getter for the name instance variable. The name of the data model.

        Returns:
            str: The textual identifier for the data model.
        """
        return self.__name

    @name.setter
    def name(
        self,
        value,
    ):
        """Setter for the name instance variable. This variable is final, please construct a new DataModel.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of name is final; it cannot be altered."
        )

    @property
    def caption(self) -> str:
        """Getter for the caption instance variable

        Returns:
            str: The caption of this model
        """
        return self.__caption

    @caption.setter
    def caption(
        self,
        value,
    ):
        """Setter for the caption instance variable. This variable is final, please construct a new DataModel.

        Args:
            value: setter cannot be used.
        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of caption is final; it cannot be altered."
        )

    @property
    def catalog(self) -> Catalog:
        """Getter for the catalog instance variable.

        Returns:
            Catalog: The Catalog object this model belongs to.
        """
        return self.__catalog

    @catalog.setter
    def catalog(
        self,
        value: Catalog,
    ):
        """Setter for catalog instance variable.

        Args:
            value (Catalog): The catalog to associate the model with.

        """
        raise atscale_errors.UnsupportedOperationException(
            "The value of catalog is final; it cannot be altered."
        )

    def get_features(
        self,
        feature_list: List[str] = None,
        folder_list: List[str] = None,
        feature_type: enums.FeatureType = enums.FeatureType.ALL,
    ) -> Dict:
        """Gets the feature names and metadata for each feature in the published DataModel.

        Args:
            feature_list (List[str], optional): A list of feature query names to return. Defaults to None to return all. All
                features in this list must exist in the model.
            folder_list (List[str], optional): A list of folders to filter by. Defaults to None to ignore folder.
            feature_type (enums.FeatureType, optional): The type of features to filter by. Options
                include enums.FeatureType.ALL, enums.FeatureType.CATEGORICAL, or enums.FeatureType.NUMERIC. Defaults to ALL.

        Returns:
            Dict: A dictionary of dictionaries where the feature names are the keys in the outer dictionary
                  while the inner keys are the following: 'data_type'(value is a level-type, 'Aggregate', or 'Calculated'),
                  'description', 'expression', caption, 'folder', and 'feature_type'(value is Numeric or Categorical).
        """
        inspection = getfullargspec(self.get_features)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_dict = metadata_helpers._get_published_features(
            self, feature_list=feature_list, folder_list=folder_list, feature_type=feature_type
        )

        # Added this gate to account for cases where feature_list is not specified
        if feature_list:
            model_validation_helpers._check_features(
                features_check_tuples=[(feature_list, private_enums.CheckFeaturesErrMsg.ALL)],
                feature_dict=ret_dict,
            )

        ret_dict = dict(sorted(ret_dict.items(), key=lambda x: x[0].upper()))
        return ret_dict

    def is_perspective(self) -> bool:
        """Checks if this DataModel is a perspective

        Returns:
            bool: true if this is a perspective
        """
        if self.__is_perspective:
            return True
        else:
            return False

    def get_fact_dataset_names(self) -> List[str]:
        """Gets the name of all fact datasets currently utilized by the DataModel and returns as a list.

        Returns:
            List[str]: list of fact dataset names
        """
        datasets = dmv_helpers._get_dmv_data(
            self,
            id_field=private_enums.Metric.dataset_name,
        )
        return sorted(list(datasets.keys()), key=lambda x: x.upper())

    def get_dimension_dataset_names(
        self,
    ) -> List[str]:
        """Gets the name of all dimension datasets currently utilized by the DataModel and returns as a list.

        Returns:
            List[str]: list of dimension dataset names
        """
        datasets = dmv_helpers._get_dmv_data(
            self,
            id_field=private_enums.Level.dataset_name,
        )
        return sorted(list(datasets.keys()), key=lambda x: x.upper())

    def get_dataset_names(self) -> List[str]:
        """Gets the name of all datasets currently utilized by the DataModel and returns as a list.

        Returns:
            List[str]: list of dataset names
        """
        names = set(self.get_dimension_dataset_names() + self.get_fact_dataset_names())
        return sorted(list(names), key=lambda x: x.upper())

    def get_dataset(self, dataset_name: str) -> Dict:
        """Gets the metadata of a dataset.

        Args:
            dataset_name (str): The name of the dataset to pull.

        Returns:
            Dict: A dictionary of the metadata for the dataset.
        """
        inspection = getfullargspec(self.get_dataset)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        dataset = dmv_helpers._get_dmv_data(
            self,
            fields=[
                private_enums.Table.dataset_name,
                private_enums.Table.database,
                private_enums.Table.db_schema,
                private_enums.Table.table,
                private_enums.Table.expression,
            ],
            id_field=private_enums.Table.dataset_name,
            filter_by={private_enums.Table.dataset_name: [dataset_name]},
        )
        ret_dict = dataset[dataset_name]
        ret_dict["used_in_fact"] = dataset_name in self.get_fact_dataset_names()
        ret_dict["used_in_dimension"] = dataset_name in self.get_dimension_dataset_names()
        return ret_dict

    def dataset_exists(self, dataset_name: str) -> bool:
        """Returns whether a given dataset_name exists in the data model, case-sensitive.

        Args:
            dataset_name (str): the name of the dataset to try and find

        Returns:
            bool: true if name found, else false.
        """
        inspection = getfullargspec(self.dataset_exists)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        return dataset_name in self.get_dataset_names()

    def get_columns(
        self,
        dataset_name: str,
    ) -> Dict:
        """Gets all currently visible columns in a given dataset, case-sensitive.

        Args:
            dataset_name (str): the name of the dataset to get columns from, case-sensitive.

        Returns:
            Dict: the columns in the given dataset
        """
        inspection = getfullargspec(self.get_columns)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if not self.dataset_exists(dataset_name):
            raise atscale_errors.ObjectNotFoundError(f"Dataset: '{dataset_name}' not found.")

        columns = dmv_helpers._get_dmv_data(
            self,
            fields=[
                private_enums.Column.data_type,
                private_enums.Column.expression,
            ],
            id_field=private_enums.Column.column_name,
            filter_by={private_enums.Column.dataset_name: [dataset_name]},
        )
        columns = dict(sorted(columns.items(), key=lambda x: x[0].upper()))
        return columns

    def column_exists(
        self,
        dataset_name: str,
        column_name: str,
    ) -> bool:
        """Checks if the given column name exists in the dataset.

        Args:
            dataset_name (str): the name of the dataset we pull the columns from, case-sensitive.
            column_name (str): the name of the column to check, case-sensitive

        Returns:
            bool: true if name found, else false.
        """
        inspection = getfullargspec(self.column_exists)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if not self.dataset_exists(dataset_name):
            raise atscale_errors.ObjectNotFoundError(f"Dataset: '{dataset_name}' not found.")

        return column_name in self.get_columns(dataset_name=dataset_name)

    def get_data(
        self,
        feature_list: List[str],
        filter_equals: Dict[str, Any] = None,
        filter_greater: Dict[str, Any] = None,
        filter_less: Dict[str, Any] = None,
        filter_greater_or_equal: Dict[str, Any] = None,
        filter_less_or_equal: Dict[str, Any] = None,
        filter_not_equal: Dict[str, Any] = None,
        filter_in: Dict[str, list] = None,
        filter_not_in: Dict[str, list] = None,
        filter_between: Dict[str, tuple] = None,
        filter_like: Dict[str, str] = None,
        filter_not_like: Dict[str, str] = None,
        filter_rlike: Dict[str, str] = None,
        filter_null: List[str] = None,
        filter_not_null: List[str] = None,
        order_by: List[Tuple[str, str]] = None,
        limit: int = None,
        comment: str = None,
        use_aggs: bool = True,
        gen_aggs: bool = True,
        fake_results: bool = False,
        use_local_cache: bool = True,
        use_aggregate_cache: bool = True,
        timeout: int = 10,
        use_postgres: bool = True,
    ) -> pd.DataFrame:
        """Submits a query against the data model using the supplied information and returns the results in a pandas DataFrame.
        Be sure that values passed to filters match the data type of the feature being filtered. Decimal precision in returned
        numeric features may differ from other variations of the get_data function.

        Args:
            feature_list (List[str]): The list of feature query names to query.
            filter_equals (Dict[str, Any], optional): Filters results based on the feature equaling the value. Defaults to None.
            filter_greater (Dict[str, Any], optional): Filters results based on the feature being greater than the value. Defaults to None.
            filter_less (Dict[str, Any], optional): Filters results based on the feature being less than the value. Defaults to None.
            filter_greater_or_equal (Dict[str, Any], optional): Filters results based on the feature being greater or equaling the value. Defaults to None.
            filter_less_or_equal (Dict[str, Any], optional): Filters results based on the feature being less or equaling the value. Defaults to None.
            filter_not_equal (Dict[str, Any], optional): Filters results based on the feature not equaling the value. Defaults to None.
            filter_in (Dict[str, list], optional): Filters results based on the feature being contained in the values. Defaults to None.
            filter_not_in (Dict[str, list], optional): Filters results based on the feature not being contained in the values. Defaults to None.
            filter_between (Dict[str, tuple], optional): Filters results based on the feature being between the values. Defaults to None.
            filter_like (Dict[str, str], optional): Filters results based on the feature being like the clause. Defaults to None.
            filter_not_like (Dict[str, str], optional): Filters results based on the feature not being like the clause. Defaults to None.
            filter_rlike (Dict[str, str], optional): Filters results based on the feature being matched by the regular expression. Defaults to None.
            filter_null (List[str], optional): Filters results to show null values of the specified features. Defaults to None.
            filter_not_null (List[str], optional): Filters results to exclude null values of the specified features. Defaults to None.
            order_by (List[Tuple[str, str]]): The sort order for the returned dataframe. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
            limit (int, optional): Limit the number of results. Defaults to None for no limit.
            comment (str, optional): A comment string to build into the query. Defaults to None for no comment.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.
            fake_results (bool, optional): Whether to use fake results, often used to train aggregates with queries
                that will frequently be used. Defaults to False.
            use_local_cache (bool, optional): Whether to allow the query to use the local cache. Defaults to True.
            use_aggregate_cache (bool, optional): Whether to allow the query to use the aggregate cache. Defaults to True.
            timeout (int, optional): The number of minutes to wait for a response before timing out. Defaults to 10.
            use_postgres (bool, optional): Whether to use Postgres dialect for inbound query. Defaults to True.

        Returns:
            DataFrame: A pandas DataFrame containing the query results.
        """
        inspection = getfullargspec(self.get_data)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        # set use_aggs and gen_aggs to True because we set them in the json when using the api
        # and this stops the flags being commented into the query
        if not use_postgres:
            if not self.catalog.repo._atconn._validate_license("FEATURE_QUERY_REST"):
                raise atscale_errors.InaccessibleAPIError(
                    "Query REST is not licensed for your AtScale server. Use postgres=True to query via JDBC."
                )
            query = query_gen_helpers._generate_atscale_query(
                data_model=self,
                feature_list=feature_list,
                filter_equals=filter_equals,
                filter_greater=filter_greater,
                filter_less=filter_less,
                filter_greater_or_equal=filter_greater_or_equal,
                filter_less_or_equal=filter_less_or_equal,
                filter_not_equal=filter_not_equal,
                filter_in=filter_in,
                filter_not_in=filter_not_in,
                filter_between=filter_between,
                filter_like=filter_like,
                filter_not_like=filter_not_like,
                filter_rlike=filter_rlike,
                filter_null=filter_null,
                filter_not_null=filter_not_null,
                order_by=order_by,
                limit=limit,
                comment=comment,
            )
            queryResponse = self.catalog.repo._atconn._post_atscale_query(
                query,
                self.catalog.name,
                use_aggs=use_aggs,
                gen_aggs=gen_aggs,
                fake_results=fake_results,
                use_local_cache=use_local_cache,
                use_aggregate_cache=use_aggregate_cache,
                timeout=timeout,
            )

            df: pd.DataFrame = request_utils.parse_rest_query_response(queryResponse)
        else:
            query = query_gen_helpers._generate_atscale_query_postgres(
                data_model=self,
                feature_list=feature_list,
                filter_equals=filter_equals,
                filter_greater=filter_greater,
                filter_less=filter_less,
                filter_greater_or_equal=filter_greater_or_equal,
                filter_less_or_equal=filter_less_or_equal,
                filter_not_equal=filter_not_equal,
                filter_in=filter_in,
                filter_not_in=filter_not_in,
                filter_between=filter_between,
                filter_like=filter_like,
                filter_not_like=filter_not_like,
                filter_rlike=filter_rlike,
                filter_null=filter_null,
                filter_not_null=filter_not_null,
                order_by=order_by,
                limit=limit,
                comment=comment,
            )

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*pandas only supports SQLAlchemy connectable",
                )
                conn = self.catalog.repo._atconn._get_postgres_conn(self)
                df = read_sql_query(query, conn)
                conn.close()

        model_validation_helpers._check_duplicate_features_get_data(feature_list)

        return df

    def get_data_direct(
        self,
        dbconn: SQLConnection,
        feature_list: List[str],
        filter_equals: Dict[str, Any] = None,
        filter_greater: Dict[str, Any] = None,
        filter_less: Dict[str, Any] = None,
        filter_greater_or_equal: Dict[str, Any] = None,
        filter_less_or_equal: Dict[str, Any] = None,
        filter_not_equal: Dict[str, Any] = None,
        filter_in: Dict[str, list] = None,
        filter_not_in: Dict[str, list] = None,
        filter_between: Dict[str, tuple] = None,
        filter_like: Dict[str, str] = None,
        filter_not_like: Dict[str, str] = None,
        filter_rlike: Dict[str, str] = None,
        filter_null: Dict[str, str] = None,
        filter_not_null: Dict[str, str] = None,
        order_by: List[Tuple[str, str]] = None,
        limit=None,
        comment=None,
        use_aggs=True,
        gen_aggs=True,
    ) -> pd.DataFrame:
        """Generates an AtScale query against the data model to get the given features, translates it to a database query, and
        submits it directly to the database using the SQLConnection. The results are returned as a Pandas DataFrame.
        Be sure that values passed to filters match the data type of the feature being filtered.Decimal precision in returned
        numeric features may differ from other variations of the get_data function.

        Args:
            dbconn (SQLConnection): The connection to use to submit the query to the database.
            feature_list (List[str]): The list of feature query names to query.
            filter_equals (Dict[str, Any], optional): A dictionary of features to filter for equality to the value. Defaults to None.
            filter_greater (Dict[str, Any], optional): A dictionary of features to filter greater than the value. Defaults to None.
            filter_less (Dict[str, Any], optional): A dictionary of features to filter less than the value. Defaults to None.
            filter_greater_or_equal (Dict[str, Any], optional): A dictionary of features to filter greater than or equal to the value. Defaults to None.
            filter_less_or_equal (Dict[str, Any], optional): A dictionary of features to filter less than or equal to the value. Defaults to None.
            filter_not_equal (Dict[str, Any], optional): A dictionary of features to filter not equal to the value. Defaults to None.
            filter_in (Dict[str, list], optional): A dictionary of features to filter in a list. Defaults to None.
            filter_not_in (Dict[str, list], optional): Filters results based on the feature not being contained in the values. Defaults to None.
            filter_between (Dict[str, tuple], optional): A dictionary of features to filter between the tuple values. Defaults to None.
            filter_like (Dict[str, str], optional): A dictionary of features to filter like the value. Defaults to None.
            filter_not_like (Dict[str, str], optional): Filters results based on the feature not being like the clause. Defaults to None.
            filter_rlike (Dict[str, str], optional): A dictionary of features to filter rlike the value. Defaults to None.
            filter_null (List[str], optional): A list of features to filter for null. Defaults to None.
            filter_not_null (List[str], optional): A list of features to filter for not null. Defaults to None.
            order_by (List[Tuple[str, str]]): The sort order for the returned dataframe. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
            limit (int, optional): A limit to put on the query. Defaults to None.
            comment (str, optional): A comment to put in the query. Defaults to None.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.

        Returns:
            DataFrame: The results of the query as a DataFrame
        """
        inspection = getfullargspec(self.get_data_direct)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())
        model_validation_helpers._validate_warehouse_connection(self, dbconn)
        df = dbconn.submit_query(
            query_gen_helpers._generate_db_query(
                data_model=self,
                atscale_query=query_gen_helpers._generate_atscale_query(
                    data_model=self,
                    feature_list=feature_list,
                    filter_equals=filter_equals,
                    filter_greater=filter_greater,
                    filter_less=filter_less,
                    filter_greater_or_equal=filter_greater_or_equal,
                    filter_less_or_equal=filter_less_or_equal,
                    filter_not_equal=filter_not_equal,
                    filter_in=filter_in,
                    filter_not_in=filter_not_in,
                    filter_between=filter_between,
                    filter_like=filter_like,
                    filter_not_like=filter_not_like,
                    filter_rlike=filter_rlike,
                    filter_null=filter_null,
                    filter_not_null=filter_not_null,
                    order_by=order_by,
                    limit=limit,
                    comment=comment,
                ),
                use_aggs=use_aggs,
                gen_aggs=gen_aggs,
            )
        )

        model_validation_helpers._check_duplicate_features_get_data(feature_list)

        return df

    def get_data_spark_jdbc(
        self,
        feature_list: List[str],
        spark_session: "SparkSession",
        jdbc_format: str,
        jdbc_options: Dict[str, str],
        filter_equals: Dict[str, Any] = None,
        filter_greater: Dict[str, Any] = None,
        filter_less: Dict[str, Any] = None,
        filter_greater_or_equal: Dict[str, Any] = None,
        filter_less_or_equal: Dict[str, Any] = None,
        filter_not_equal: Dict[str, Any] = None,
        filter_in: Dict[str, list] = None,
        filter_not_in: Dict[str, list] = None,
        filter_between: Dict[str, tuple] = None,
        filter_like: Dict[str, str] = None,
        filter_not_like: Dict[str, str] = None,
        filter_rlike: Dict[str, str] = None,
        filter_null: List[str] = None,
        filter_not_null: List[str] = None,
        order_by: List[Tuple[str, str]] = None,
        limit: int = None,
        comment: str = None,
        use_aggs=True,
        gen_aggs=True,
    ):
        """Uses the provided information to establish a jdbc connection to the underlying data warehouse. Generates a query against the data model and uses
        the provided spark_session to execute. Returns the results in a spark DataFrame. Be sure that values passed to filters match the data type of the
        feature being filtered. Decimal precision in returned numeric features may differ from other variations of the get_data function.

        Args:
            feature_list (List[str]): The list of feature query names to query.
            spark_session (pyspark.sql.SparkSession): The pyspark SparkSession to execute the query with
            jdbc_format (str): the driver class name. For example: 'jdbc', 'net.snowflake.spark.snowflake', 'com.databricks.spark.redshift'
            jdbc_options (Dict[str,str]): Case-insensitive to specify connection options for jdbc
            filter_equals (Dict[str, Any], optional): Filters results based on the feature equaling the value. Defaults to None.
            filter_greater (Dict[str, Any], optional): Filters results based on the feature being greater than the value. Defaults to None.
            filter_less (Dict[str, Any], optional): Filters results based on the feature being less than the value. Defaults to None.
            filter_greater_or_equal (Dict[str, Any], optional): Filters results based on the feature being greater or equaling the value. Defaults to None.
            filter_less_or_equal (Dict[str, Any], optional): Filters results based on the feature being less or equaling the value. Defaults to None.
            filter_not_equal (Dict[str, Any], optional): Filters results based on the feature not equaling the value. Defaults to None.
            filter_in (Dict[str, list], optional): Filters results based on the feature being contained in the values. Defaults to None.
            filter_not_in (Dict[str, list], optional): Filters results based on the feature not being contained in the values. Defaults to None.
            filter_between (Dict[str, tuple], optional): Filters results based on the feature being between the values. Defaults to None.
            filter_like (Dict[str, str], optional): Filters results based on the feature being like the clause. Defaults to None.
            filter_not_like (Dict[str, str], optional): Filters results based on the feature not being like the clause. Defaults to None.
            filter_rlike (Dict[str, str], optional): Filters results based on the feature being matched by the regular expression. Defaults to None.
            filter_null (List[str], optional): Filters results to show null values of the specified features. Defaults to None.
            filter_not_null (List[str], optional): Filters results to exclude null values of the specified features. Defaults to None.
            order_by (List[Tuple[str, str]]): The sort order for the returned dataframe. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
            limit (int, optional): Limit the number of results. Defaults to None for no limit.
            comment (str, optional): A comment string to build into the query. Defaults to None for no comment.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.

        Returns:
            pyspark.sql.dataframe.DataFrame: A pyspark DataFrame containing the query results.
        """
        inspection = getfullargspec(self.get_data_spark_jdbc)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        try:
            from pyspark.sql import SparkSession
        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("spark", str(e))

        query = query_gen_helpers._generate_db_query(
            self,
            query_gen_helpers._generate_atscale_query(
                data_model=self,
                feature_list=feature_list,
                filter_equals=filter_equals,
                filter_greater=filter_greater,
                filter_less=filter_less,
                filter_greater_or_equal=filter_greater_or_equal,
                filter_less_or_equal=filter_less_or_equal,
                filter_not_equal=filter_not_equal,
                filter_in=filter_in,
                filter_not_in=filter_not_in,
                filter_between=filter_between,
                filter_like=filter_like,
                filter_not_like=filter_not_like,
                filter_rlike=filter_rlike,
                filter_null=filter_null,
                filter_not_null=filter_not_null,
                order_by=order_by,
                limit=limit,
                comment=comment,
            ),
            use_aggs=use_aggs,
            gen_aggs=gen_aggs,
        )

        logger.info(
            f"get_data_spark_jdbc is only compatible with databricks runtimes >=13.0. Versions less than this will have issues with their built in jdbc drivers."
        )
        df = (
            spark_session.read.format(jdbc_format)
            .options(**jdbc_options)
            .option("query", query)
            .load()
        )

        column_index = range(len(df.columns))
        column_names = df.columns

        for column in column_index:
            df = df.withColumnRenamed(column_names[column], feature_list[column])

        return df

    def get_data_spark(
        self,
        feature_list: List[str],
        spark_session,
        filter_equals: Dict[str, Any] = None,
        filter_greater: Dict[str, Any] = None,
        filter_less: Dict[str, Any] = None,
        filter_greater_or_equal: Dict[str, Any] = None,
        filter_less_or_equal: Dict[str, Any] = None,
        filter_not_equal: Dict[str, Any] = None,
        filter_in: Dict[str, list] = None,
        filter_not_in: Dict[str, list] = None,
        filter_between: Dict[str, tuple] = None,
        filter_like: Dict[str, str] = None,
        filter_not_like: Dict[str, str] = None,
        filter_rlike: Dict[str, str] = None,
        filter_null: List[str] = None,
        filter_not_null: List[str] = None,
        order_by: List[Tuple[str, str]] = None,
        limit: int = None,
        comment: str = None,
        use_aggs=True,
        gen_aggs=True,
    ):
        """Uses the provided spark_session to execute a query generated by the AtScale query engine against the data model.
        Returns the results in a spark DataFrame. Be sure that values passed to filters match the data type of the feature
        being filtered. Decimal precision in returned numeric features may differ from other variations of the get_data function.

        Args:
            feature_list (List[str]): The list of feature query names to query.
            spark_session (pyspark.sql.SparkSession): The pyspark SparkSession to execute the query with
            filter_equals (Dict[str, Any], optional): Filters results based on the feature equaling the value. Defaults to None.
            filter_greater (Dict[str, Any], optional): Filters results based on the feature being greater than the value. Defaults to None.
            filter_less (Dict[str, Any], optional): Filters results based on the feature being less than the value. Defaults to None.
            filter_greater_or_equal (Dict[str, Any], optional): Filters results based on the feature being greater or equaling the value. Defaults to None.
            filter_less_or_equal (Dict[str, Any], optional): Filters results based on the feature being less or equaling the value. Defaults to None.
            filter_not_equal (Dict[str, Any], optional): Filters results based on the feature not equaling the value. Defaults to None.
            filter_in (Dict[str, list], optional): Filters results based on the feature being contained in the values. Defaults to None.
            filter_not_in (Dict[str, list], optional): Filters results based on the feature not being contained in the values. Defaults to None.
            filter_between (Dict[str, tuple], optional): Filters results based on the feature being between the values. Defaults to None.
            filter_like (Dict[str, str], optional): Filters results based on the feature being like the clause. Defaults to None.
            filter_not_like (Dict[str, str], optional): Filters results based on the feature not being like the clause. Defaults to None.
            filter_rlike (Dict[str, str], optional): Filters results based on the feature being matched by the regular expression. Defaults to None.
            filter_null (List[str], optional): Filters results to show null values of the specified features. Defaults to None.
            filter_not_null (List[str], optional): Filters results to exclude null values of the specified features. Defaults to None.
            order_by (List[Tuple[str, str]]): The sort order for the returned dataframe. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
            limit (int, optional): Limit the number of results. Defaults to None for no limit.
            comment (str, optional): A comment string to build into the query. Defaults to None for no comment.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.

        Returns:
            pyspark.sql.dataframe.DataFrame: A pyspark DataFrame containing the query results.
        """
        inspection = getfullargspec(self.get_data_spark)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        try:
            from pyspark.sql import SparkSession
        except ImportError as e:
            raise atscale_errors.AtScaleExtrasDependencyImportError("spark", str(e))

        query = query_gen_helpers._generate_db_query(
            self,
            query_gen_helpers._generate_atscale_query(
                data_model=self,
                feature_list=feature_list,
                filter_equals=filter_equals,
                filter_greater=filter_greater,
                filter_less=filter_less,
                filter_greater_or_equal=filter_greater_or_equal,
                filter_less_or_equal=filter_less_or_equal,
                filter_not_equal=filter_not_equal,
                filter_in=filter_in,
                filter_not_in=filter_not_in,
                filter_between=filter_between,
                filter_like=filter_like,
                filter_not_like=filter_not_like,
                filter_rlike=filter_rlike,
                filter_null=filter_null,
                filter_not_null=filter_not_null,
                order_by=order_by,
                limit=limit,
                comment=comment,
            ),
            use_aggs=use_aggs,
            gen_aggs=gen_aggs,
        )

        # ok here I want to call a sqlconn function that optionally can adjust the default catalog/database of the session and then revert it
        df = spark_session.sql(query)

        column_index = range(len(df.columns))
        column_names = df.columns

        for column in column_index:
            df = df.withColumnRenamed(column_names[column], feature_list[column])

        model_validation_helpers._check_duplicate_features_get_data(feature_list)

        return df

    def get_database_query(
        self,
        feature_list: List[str],
        filter_equals: Dict[str, Any] = None,
        filter_greater: Dict[str, Any] = None,
        filter_less: Dict[str, Any] = None,
        filter_greater_or_equal: Dict[str, Any] = None,
        filter_less_or_equal: Dict[str, Any] = None,
        filter_not_equal: Dict[str, Any] = None,
        filter_in: Dict[str, list] = None,
        filter_not_in: Dict[str, list] = None,
        filter_between: Dict[str, tuple] = None,
        filter_like: Dict[str, str] = None,
        filter_not_like: Dict[str, str] = None,
        filter_rlike: Dict[str, str] = None,
        filter_null: List[str] = None,
        filter_not_null: List[str] = None,
        order_by: List[Tuple[str, str]] = None,
        limit: int = None,
        comment: str = None,
        use_aggs: bool = True,
        gen_aggs: bool = True,
    ) -> str:
        """Returns a database query generated using the data model to get the given features. Be sure that values passed to filters match the data
        type of the feature being filtered.

        Args:
            feature_list (List[str]): The list of feature query names to query.
            filter_equals (Dict[str, Any], optional): A dictionary of features to filter for equality to the value. Defaults to None.
            filter_greater (Dict[str, Any], optional): A dictionary of features to filter greater than the value. Defaults to None.
            filter_less (Dict[str, Any], optional): A dictionary of features to filter less than the value. Defaults to None.
            filter_greater_or_equal (Dict[str, Any], optional): A dictionary of features to filter greater than or equal to the value. Defaults to None.
            filter_less_or_equal (Dict[str, Any], optional): A dictionary of features to filter less than or equal to the value. Defaults to None.
            filter_not_equal (Dict[str, Any], optional): A dictionary of features to filter not equal to the value. Defaults to None.
            filter_in (Dict[str, list], optional): A dictionary of features to filter in a list. Defaults to None.
            filter_not_in (Dict[str, list], optional): A dictionary of features to filter not in a list. Defaults to None.
            filter_between (Dict[str, tuple], optional): A dictionary of features to filter between the tuple values. Defaults to None.
            filter_like (Dict[str, str], optional): A dictionary of features to filter like the value. Defaults to None.
            filter_not_like (Dict[str, str], optional): A dictionary of features to filter not like the value. Defaults to None.
            filter_rlike (Dict[str, str], optional): A dictionary of features to filter rlike the value. Defaults to None.
            filter_null (List[str], optional): A list of features to filter for null. Defaults to None.
            filter_not_null (List[str], optional): A list of features to filter for not null. Defaults to None.
            order_by (List[Tuple[str, str]]): The sort order for the returned query. Accepts a list of tuples of the
                feature query name and ordering respectively: [('feature_name_1', 'DESC'), ('feature_2', 'ASC') ...].
                Defaults to None for AtScale Engine default sorting.
            limit (int, optional): A limit to put on the query. Defaults to None.
            comment (str, optional): A comment to put in the query. Defaults to None.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.

        Returns:
            str: The generated database query
        """
        inspection = getfullargspec(self.get_database_query)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        return query_gen_helpers._generate_db_query(
            data_model=self,
            atscale_query=query_gen_helpers._generate_atscale_query(
                data_model=self,
                feature_list=feature_list,
                filter_equals=filter_equals,
                filter_greater=filter_greater,
                filter_less=filter_less,
                filter_greater_or_equal=filter_greater_or_equal,
                filter_less_or_equal=filter_less_or_equal,
                filter_not_equal=filter_not_equal,
                filter_in=filter_in,
                filter_not_in=filter_not_in,
                filter_between=filter_between,
                filter_like=filter_like,
                filter_not_like=filter_not_like,
                filter_rlike=filter_rlike,
                filter_null=filter_null,
                filter_not_null=filter_not_null,
                order_by=order_by,
                limit=limit,
                comment=comment,
            ),
            use_aggs=use_aggs,
            gen_aggs=gen_aggs,
        )

    def submit_atscale_query(
        self,
        query: str,
        use_aggs: bool = True,
        gen_aggs: bool = True,
        fake_results: bool = False,
        use_local_cache: bool = True,
        use_aggregate_cache: bool = True,
        use_postgres: bool = True,
        timeout: int = 10,
    ) -> pd.DataFrame:
        """Submits the given query against the data model and returns the results in a pandas DataFrame.

        Args:
            query (str): The SQL query to submit.
            use_aggs (bool, optional): Whether to allow the query to use aggs. Defaults to True.
            gen_aggs (bool, optional): Whether to allow the query to generate aggs. Defaults to True.
            fake_results (bool, optional): Whether to use fake results, often used to train aggregates with queries
                that will frequently be used. Defaults to False.
            use_local_cache (bool, optional): Whether to allow the query to use the local cache. Defaults to True.
            use_aggregate_cache (bool, optional): Whether to allow the query to use the aggregate cache. Defaults to True.
            use_postgres (bool, optional): Whether to use Postgres dialect for inbound query. Defaults to True.
            timeout (int, optional): The number of minutes to wait for a response before timing out. Defaults to 10.

        Returns:
            DataFrame: A pandas DataFrame containing the query results.
        """
        inspection = getfullargspec(self.submit_atscale_query)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        if use_postgres:
            if not use_aggs:
                query = query + " /* use_aggs(false) */"
            if not gen_aggs:
                query = query + " /* generate_aggs(false) */"
            if fake_results:
                query = query + " /* fake_results(true) */"
            if not use_local_cache:
                query = query + " /* use_local_cache(false) */"
            if not use_aggregate_cache:
                query = query + " /* use_aggregate_cache(false) */"
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*pandas only supports SQLAlchemy connectable",
                )
                conn = self.catalog.repo._atconn._get_postgres_conn(self)
                df = read_sql_query(query, conn)
                conn.close()
        else:
            if not self.catalog.repo._atconn._validate_license("FEATURE_QUERY_REST"):
                raise atscale_errors.InaccessibleAPIError(
                    "Query REST is not licensed for your AtScale server. Use postgres=True to query via JDBC."
                )
            queryResponse = self.catalog.repo._atconn._post_atscale_query(
                query,
                self.catalog.name,
                use_aggs=use_aggs,
                gen_aggs=gen_aggs,
                fake_results=fake_results,
                use_local_cache=use_local_cache,
                use_aggregate_cache=use_aggregate_cache,
                timeout=timeout,
            )

            df: pd.DataFrame = request_utils.parse_rest_query_response(queryResponse)

        return df

    def validate_mdx(self, expression: str) -> bool:
        """Verifies if the given MDX Expression is valid for the current data model.

        Args:
            expression (str): The MDX expression for the feature.

        Returns:
            bool: Returns True if mdx is valid.
        """
        response = model_validation_helpers._validate_mdx_syntax(
            self.catalog.repo._atconn, expression, raises=False
        )
        if response == "":
            return True
        else:
            return False

    def get_dimensions(self) -> Dict:
        """Gets a dictionary of dictionaries with the published dimension names and metadata.

        Returns:
            Dict: A dictionary of dictionaries where the dimension names are the keys in the outer dictionary
                while the inner keys are the following: 'description', 'type'(value is Time or Standard).
        """
        filter_by = {}
        ret_dict = metadata_helpers._get_dimensions(self, filter_by=filter_by)
        ret_dict = dict(sorted(ret_dict.items(), key=lambda x: x[0].upper()))
        return ret_dict

    def get_hierarchies(
        self,
        secondary_attribute: bool = False,
        folder_list: List[str] = None,
    ) -> Dict:
        """Gets a dictionary of dictionaries with the published hierarchy names and metadata. Secondary attributes are treated as
             their own hierarchies, they are hidden by default, but can be shown with the secondary_attribute parameter.

        Args:
            secondary_attribute (bool, optional): if we want to filter the secondary attribute field. True will return hierarchies and
                secondary_attributes, False will return only non-secondary attributes. Defaults to False.
            folder_list (List[str], optional): The list of folders in the data model containing hierarchies to exclusively list.
                Defaults to None to not filter by folder.

        Returns:
            Dict: A dictionary of dictionaries where the hierarchy names are the keys in the outer dictionary
                while the inner keys are the following: 'dimension', 'description', 'caption', 'folder', 'type'(value is
                Time or Standard), 'secondary_attribute'.
        """
        inspection = getfullargspec(self.get_hierarchies)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        filter_by = {}
        if not secondary_attribute:
            filter_by[private_enums.Hierarchy.secondary_attribute] = [False]

        # folder list is more involved as we need to append if the dict already exists
        if folder_list is not None:
            if type(folder_list) == str:
                folder_list = [folder_list]
            filter_by[private_enums.Hierarchy.folder] = folder_list
        ret_dict = metadata_helpers._get_hierarchies(self, filter_by=filter_by)

        ret_dict = dict(sorted(ret_dict.items(), key=lambda x: x[0].upper()))
        return ret_dict

    def get_hierarchy_levels(
        self,
        hierarchy_name: str,
    ) -> List[str]:
        """Gets a list of strings for the levels of a given published hierarchy

        Args:
            hierarchy_name (str): The query name of the hierarchy

        Returns:
            List[str]: A list containing the hierarchy's levels
        """
        inspection = getfullargspec(self.get_hierarchy_levels)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = metadata_helpers._get_hierarchy_levels(self, hierarchy_name)

        if ret_list == []:
            raise atscale_errors.ObjectNotFoundError(f'No hierarchy named "{hierarchy_name}" found')

        return sorted(ret_list, key=lambda x: x.upper())

    def get_secondary_attributes_at_level(
        self,
        level: str,
    ) -> List[str]:
        """Gets the secondary attributes that are tied to the provided level

        Args:
            level (str): The level in question

        Returns:
            List[str]: A list of attribute names
        """
        if not self.catalog.repo._atconn._validate_license("FEATURE_DATA_CATALOG_API"):
            raise atscale_errors.InaccessibleAPIError(
                "Data Catalog API is not licensed for your AtScale server. Unable to pull the metadata needed."
            )
        inspection = getfullargspec(self.get_secondary_attributes_at_level)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        existing_features = metadata_helpers._get_published_features(
            data_model=self,
            feature_type=enums.FeatureType.CATEGORICAL,
        )

        model_validation_helpers._check_features(
            features_check_tuples=[([level], private_enums.CheckFeaturesErrMsg.CATEGORICAL)],
            feature_dict=existing_features,
        )

        dmv_resp = dmv_helpers._get_dmv_data(
            model=self,
            fields=[private_enums.Level.level_guid, private_enums.Level.parent_level_id],
            id_field=private_enums.Level.name,
        )

        # just grabbing the part of the string before `+`; it seems that roleplayed levels are suffixed as such
        level_id = dmv_resp.get(level).get("level_guid").split("+")[0]

        # i.e. return the levels whose parent is the input level, which are secondary attributes (to
        # exclude aliases, etc.), and which are of the same dimension as the input level (to account for cases
        # where the input level's original level has been roleplayed multiple times; we don't want to return
        # levels safe to query only at another roleplay of the original level)
        return [
            x
            for x in dmv_resp
            if dmv_resp.get(x).get("parent_level_id") == level_id
            and existing_features.get(x).get("secondary_attribute")
            and existing_features.get(x).get("dimension")
            == existing_features.get(level).get("dimension")
        ]

    def get_feature_description(
        self,
        feature: str,
    ) -> str:
        """Returns the description of a given published feature.

        Args:
            feature (str): The query name of the feature to retrieve the description of.

        Returns:
            str: The description of the given feature.
        """
        inspection = getfullargspec(self.get_feature_description)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        existing_features = metadata_helpers._get_published_features(
            data_model=self, feature_list=[feature]
        )

        model_validation_helpers._check_features(
            features_check_tuples=[([feature], private_enums.CheckFeaturesErrMsg.ALL)],
            feature_dict=existing_features,
        )

        feature_description = existing_features[feature].get("description", "")
        return feature_description

    def get_feature_expression(
        self,
        feature: str,
    ) -> str:
        """Returns the expression of a given published feature.

        Args:
            feature (str): The query name of the feature to return the expression of.

        Returns:
            str: The expression of the given feature.
        """
        inspection = getfullargspec(self.get_feature_expression)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        existing_features = metadata_helpers._get_published_features(
            data_model=self, feature_list=[feature]
        )

        model_validation_helpers._check_features(
            features_check_tuples=[([feature], private_enums.CheckFeaturesErrMsg.ALL)],
            feature_dict=existing_features,
        )

        return existing_features[feature].get("expression", "")

    def get_all_numeric_feature_names(
        self,
        folder: str = None,
    ) -> List[str]:
        """Returns a list of all published numeric features (ie Aggregate and Calculated Metrics) in the data model.

        Args:
            folder (str, optional): The name of a folder in the data model containing metrics to exclusively list.
                Defaults to None to not filter by folder.

        Returns:
            List[str]: A list of the query names of numeric features in the data model and, if given, in the folder.
        """
        inspection = getfullargspec(self.get_all_numeric_feature_names)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = metadata_helpers._get_all_numeric_feature_names(self, folder=folder)
        return sorted(ret_list, key=lambda x: x.upper())

    def get_all_categorical_feature_names(
        self,
        folder: str = None,
    ) -> List[str]:
        """Returns a list of all published categorical features (ie Hierarchy levels and secondary_attributes) in the given DataModel.

        Args:
            folder (str, optional): The name of a folder in the DataModel containing features to exclusively list.
                Defaults to None to not filter by folder.

        Returns:
            List[str]: A list of the query names of categorical features in the DataModel and, if given, in the folder.
        """
        inspection = getfullargspec(self.get_all_categorical_feature_names)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        ret_list = metadata_helpers._get_all_categorical_feature_names(self, folder=folder)
        return sorted(ret_list, key=lambda x: x.upper())

    def get_folders(self) -> List[str]:
        """Returns a list of the available folders in the published DataModel.

        Returns:
            List[str]: A list of the available folders
        """
        ret_list = metadata_helpers._get_folders(self)
        return sorted(ret_list, key=lambda x: x.upper())

    def get_connected_warehouse(
        self,
    ) -> Dict:
        """Returns the warehouse info utilized in this data_model

        Returns:
            Dict: A dictionary describing the connected warehouse
        """
        conn = list(
            dmv_helpers._get_dmv_data(
                self,
                id_field=private_enums.Table.connection_id,
            ).keys()
        )[0]

        current_warehouse = {}

        warehouses = self.catalog.repo._atconn._get_connection_groups()
        for ind, wh in enumerate(warehouses):
            ret_dict = wh.__dict__
            ret_dict["platform"] = ret_dict["platform_type"]._value_
            del ret_dict["platform_type"]

            if ret_dict["connection_id"] == conn:
                current_warehouse = ret_dict

        return current_warehouse

    def generate_time_series_features(
        self,
        dataframe: pd.DataFrame,
        numeric_features: List[str],
        time_hierarchy: str,
        level: str,
        group_features: List[str] = None,
        intervals: List[int] = None,
        shift_amount: int = 0,
    ) -> pd.DataFrame:
        """Generates time series features off of the data model, like rolling statistics and period to date for the given numeric features
        using the time hierarchy from the given data model. The core of the function is built around the groupby function, like so:
            dataframe[groupby(group_features + hierarchy_levels)][shift(shift_amount)][rolling(interval)][{aggregate function}]

        Args:
            dataframe (pandas.DataFrame): the pandas dataframe with the features.
            numeric_features (List[str]): The list of numeric feature query names to build time series features of.
            time_hierarchy (str): The query names of the time hierarchy to use to derive features.
            level (str): The query name of the level within the time hierarchy to derive the features at.
            group_features (List[str], optional): The list of features to group by. Note that this acts as a logical grouping as opposed to a
                dimensionality reduction when paired with shifts or intervals. Defaults to None.
            intervals (List[int], optional): The intervals to create the features over.
                Will use default values based on the time step of the given level if None. Defaults to None.
            shift_amount (int, optional): The amount of rows to shift the new features. Defaults to 0.

        Returns:
            DataFrame: A DataFrame containing the original columns and the newly generated ones
        """
        inspection = getfullargspec(self.generate_time_series_features)
        validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

        # TODO update and uncomment
        # feature_utils._check_time_hierarchy(
        #     data_model=data_model, hierarchy_name=time_hierarchy, level_name=level
        # )

        all_published_features = self.get_features()

        numeric_list = []
        categorical_list = []
        for name, info in all_published_features:
            if info["feature_type"] == enums.FeatureType.NUMERIC.name_val:
                numeric_list.append(name)
            else:
                categorical_list.append(name)

        if group_features:
            model_validation_helpers._check_features(
                features_check_tuples=[
                    (group_features, private_enums.CheckFeaturesErrMsg.CATEGORICAL)
                ],
                feature_dict=all_published_features,
            )

        model_validation_helpers._check_features(
            features_check_tuples=[(numeric_features, private_enums.CheckFeaturesErrMsg.NUMERIC)],
            feature_dict=all_published_features,
        )

        level_dict = all_published_features[level]
        time_numeric = level_dict["atscale_type"]
        # takes out the Time and 's' at the end and in lowercase
        time_name = str(time_numeric)[4:-1].lower()

        if intervals:
            if type(intervals) != list:
                intervals = [intervals]
        else:
            intervals = enums.TimeSteps[time_numeric]._get_steps()

        shift_name = f"_shift_{shift_amount}" if shift_amount != 0 else ""

        levels = [
            x
            for x in metadata_helpers._get_hierarchy_levels(self, time_hierarchy)
            if x in dataframe.columns
        ]

        if group_features:
            dataframe = dataframe.sort_values(by=group_features + levels).reset_index(drop=True)
        else:
            dataframe = dataframe.sort_values(by=levels).reset_index(drop=True)

        for feature in numeric_features:
            if group_features:

                def grouper(x):
                    return x.groupby(group_features)

            else:

                def grouper(x):
                    return x

                # set this to an empty list so we can add it to hier_level later no matter what
                group_features = []

            # a helper function for the agg chaining
            def groupby_chain(
                dataframe_n, feature_n, group_func, shift_amt, roll_interval, agg_func
            ):
                if shift_amount != 0:
                    func_to_exec = getattr(
                        group_func(dataframe_n)[feature_n].shift(shift_amt).rolling(roll_interval),
                        agg_func,
                    )
                    return func_to_exec().reset_index(drop=True)
                else:
                    func_to_exec = getattr(
                        group_func(dataframe_n)[feature_n].rolling(roll_interval), agg_func
                    )
                    return func_to_exec().reset_index(drop=True)

            for interval in intervals:
                interval = int(interval)
                name = feature + f"_{interval}_{time_name}_"

                if interval > 1:
                    dataframe[f"{name}sum{shift_name}"] = groupby_chain(
                        dataframe, feature, grouper, shift_amount, interval, "sum"
                    )

                    dataframe[f"{name}avg{shift_name}"] = groupby_chain(
                        dataframe, feature, grouper, shift_amount, interval, "mean"
                    )

                    dataframe[f"{name}stddev{shift_name}"] = groupby_chain(
                        dataframe, feature, grouper, shift_amount, interval, "std"
                    )

                    dataframe[f"{name}min{shift_name}"] = groupby_chain(
                        dataframe, feature, grouper, shift_amount, interval, "min"
                    )

                    dataframe[f"{name}max{shift_name}"] = groupby_chain(
                        dataframe, feature, grouper, shift_amount, interval, "max"
                    )

                dataframe[f"{name}lag{shift_name}"] = (
                    grouper(dataframe)[feature]
                    .shift(shift_amount + interval)
                    .reset_index(drop=True)
                )

            found = False
            for heir_level in reversed(levels):
                if found and heir_level in dataframe.columns:
                    name = f"{feature}_{heir_level}_to_date"
                    if shift_amount != 0:
                        dataframe[name] = (
                            dataframe.groupby(group_features + [heir_level])[feature]
                            .shift(shift_amount)
                            .cumsum()
                            .reset_index(drop=True)
                        )
                    else:
                        dataframe[name] = (
                            dataframe.groupby(group_features + [heir_level])[feature]
                            .cumsum()
                            .reset_index(drop=True)
                        )
                if heir_level == level:
                    found = True

        return dataframe
