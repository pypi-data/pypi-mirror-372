from inspect import getfullargspec
from aenum import Enum, NoAlias

from atscale.base.enums import TimeSteps, Aggs
from atscale.utils import validation_utils


class DMVColumnBaseClass(Enum):
    """The base class for our various dmv query enums. Defines consistent functionality."""

    def requires_translation(self):
        if self in self.internal_func_dict():
            return True
        return False

    def to_regex(self):
        return f"<{self.value}>(.*?)</{self.value}>"

    def translate(
        self,
        val,
    ):
        """Translates the parsed output from a DMV response into a user interpretable format. If a field has a specific
        translation, Hierarcy.dimension: [dimension_name] -> dimension_name for example, it must be declared in the
        respective class's internal_func_dict() method."""
        func_dict = self.internal_func_dict()
        if self in func_dict:
            func = func_dict[self]
            return func(val)
        else:
            return val


class Dimension(DMVColumnBaseClass):
    """An enum to represent the metadata of a dimension object for use in dmv queries.
    description: the description field
    name: the name field
    type: the type field
    visible: the visible field
    """

    description = "DESCRIPTION"
    name = "DIMENSION_NAME"
    visible = "DIMENSION_IS_VISIBLE"
    type = "DIMENSION_TYPE"

    @property
    def schema(self):
        return "$system.MDSCHEMA_DIMENSIONS"

    @property
    def where(self):
        return " WHERE [DIMENSION_NAME] &lt;&gt; 'Measures' AND [CUBE_NAME] = @CubeName"

    def internal_func_dict(self):
        def hierarchy_type_func(type_number: str):
            inspection = getfullargspec(hierarchy_type_func)
            validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

            if type_number == "1":
                return "Time"
            elif type_number == "3":
                return "Standard"
            else:
                return None

        return {self.__class__.type: (lambda x: hierarchy_type_func(x))}


class Hierarchy(DMVColumnBaseClass):
    """An enum to represent the metadata of a hierarchy object for use in dmv queries.
    description: the description field
    name: the name field
    caption: the caption field
    visible: the visible field
    type: the type field
    folder: the folder field
    dimension: the dimension field
    secondary_attribute: the secondary_attribute field
    """

    description = "DESCRIPTION"
    name = "HIERARCHY_NAME"
    caption = "HIERARCHY_CAPTION"
    visible = "HIERARCHY_IS_VISIBLE"
    type = "DIMENSION_TYPE"
    folder = "HIERARCHY_DISPLAY_FOLDER"
    dimension = "DIMENSION_UNIQUE_NAME"
    secondary_attribute = "HIERARCHY_ORIGIN"

    @property
    def schema(self):
        return "$system.MDSCHEMA_HIERARCHIES"

    @property
    def where(self):
        return " WHERE [HIERARCHY_NAME] &lt;&gt; 'Measures' AND [CUBE_NAME] = @CubeName"

    def internal_func_dict(self):
        def hierarchy_type_func(type_number: str):
            inspection = getfullargspec(hierarchy_type_func)
            validation_utils.validate_by_type_hints(inspection=inspection, func_params=locals())

            if type_number == "1":
                return "Time"
            elif type_number == "3":
                return "Standard"
            else:
                return None

        return {
            self.__class__.type: (lambda x: hierarchy_type_func(x)),
            self.__class__.dimension: (lambda x: x[1:-1]),
            self.__class__.secondary_attribute: (lambda x: False if x == "1" else True),
        }


class Metric(DMVColumnBaseClass):
    """An enum to represent the metadata of a metric object for use in dmv queries.
    name: the name field
    description: the description field
    caption: the caption field
    visible: the visible field
    type: the type field
    folder: the folder field
    expression: the expression field
    """

    name = "MEASURE_NAME"
    description = "DESCRIPTION"
    caption = "MEASURE_CAPTION"
    visible = "MEASURE_IS_VISIBLE"
    type = "MEASURE_AGGREGATOR"
    folder = "MEASURE_DISPLAY_FOLDER"
    expression = "EXPRESSION"
    data_type = "DATA_TYPE"
    dataset_name = "DATASET_NAME"

    @property
    def schema(self):
        return "$system.MDSCHEMA_MEASURES"

    @property
    def where(self):
        return " WHERE [CUBE_NAME] = @CubeName"  # need to specify only fields for our cube for all query types

    def internal_func_dict(self):
        return {
            self.__class__.type: (
                lambda x: "Calculated" if x == "9" else Aggs._from_dmv_number(int(x))._visual_rep
            ),
            self.__class__.data_type: (lambda x: DBDataType(int(x)).name),
        }


class Level(DMVColumnBaseClass):
    """An enum to represent the metadata of a level object for use in dmv queries.
    description: the description field
    name: the name field
    caption: the caption field
    visible: the visible field
    type: the type field
    dimension: the dimension field
    hierarchy: the hierarchy field
    level_number: the level_number field
    """

    _settings_ = NoAlias  # necessary for different fields with the same value but different func

    description = "DESCRIPTION"
    name = "LEVEL_NAME"
    caption = "LEVEL_CAPTION"
    visible = "LEVEL_IS_VISIBLE"
    type = "LEVEL_TYPE"
    dimension = "HIERARCHY_UNIQUE_NAME"
    hierarchy = "HIERARCHY_UNIQUE_NAME"
    level_number = "LEVEL_NUMBER"
    data_type = "LEVEL_DBTYPE"
    secondary_attribute = "IS_PRIMARY"
    dataset_name = "DATASET_NAME"
    parent_level_id = "PARENT_LEVEL_ID"
    level_guid = "LEVEL_GUID"

    @property
    def schema(self):
        return "$system.mdschema_levels"

    @property
    def where(self):
        return (
            " WHERE [CUBE_NAME] = @CubeName and [LEVEL_NAME] &lt;&gt; '(All)' and [DIMENSION_UNIQUE_NAME] "
            "&lt;&gt; '[Measures]'"
        )

    def internal_func_dict(self):
        return {
            self.__class__.level_number: (lambda x: int(x)),
            self.__class__.hierarchy: (lambda x: x.split("].[")[1][:-1]),
            self.__class__.dimension: (lambda x: x.split("].[")[0][1:]),
            self.__class__.type: (lambda x: TimeSteps(int(x)).name),
            self.__class__.data_type: (lambda x: DBDataType(int(x)).name),
            self.__class__.secondary_attribute: (lambda x: x == "false"),
        }


class Table(DMVColumnBaseClass):
    """An enum to represent the metadata of a table object for use in dmv queries.
    description: the description field
    name: the name field
    type: the type field
    visible: the visible field
    """

    catalog_name = "CATALOG_NAME"
    cube_id = "CUBE_GUID"
    connection_id = "CONNECTION_ID"
    dataset_name = "DATASET_NAME"
    database = "DATABASE"
    db_schema = "SCHEMA"
    table = "TABLE"
    expression = "EXPRESSION"

    @property
    def schema(self):
        return "$system.DBSCHEMA_TABLES"

    @property
    def where(self):
        return ""

    def internal_func_dict(self):
        return {}


class Column(DMVColumnBaseClass):
    """An enum to represent the metadata of a column object for use in dmv queries.
    description: the description field
    name: the name field
    type: the type field
    visible: the visible field
    """

    catalog_name = "CATALOG_NAME"
    dataset_name = "DATASET_NAME"
    column_name = "COLUMN_NAME"
    data_type = "DATA_TYPE"
    expression = "EXPRESSION"

    @property
    def schema(self):
        return "$system.DBSCHEMA_COLUMNS"

    @property
    def where(self):
        return ""

    def internal_func_dict(self):
        return {self.__class__.data_type: (lambda x: DBDataType(int(x)).name)}


class DBDataType(Enum):
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    EMPTY = 0  # Indicates that no value was specified.
    INT1 = 16  # Indicates a one-byte signed integer.
    INT2 = 2  # Indicates a two-byte signed integer.
    INT4 = 3  # Indicates a four-byte signed integer.
    INT8 = 20  # Indicates an eight-byte signed integer.
    INT_UNSIGNED1 = 17  # Indicates a one-byte unsigned integer.
    INT_UNSIGNED2 = 18  # Indicates a two-byte unsigned integer.
    INT_UNSIGNED4 = 19  # Indicates a four-byte unsigned integer.
    INT_UNSIGNED8 = 21  # Indicates an eight-byte unsigned integer.
    FLOAT32 = 4  # Indicates a single-precision floating-point value.
    FLOAT64 = 5  # Indicates a double-precision floating-point value.
    CURRENCY = 6  # Indicates a currency value. Currency is a fixed-point number with four digits to the right of the decimal point and is stored in an eight-byte signed integer scaled by 10,000.
    DATE_DOUBLE = 7  # Indicates a date value. Date values are stored as Double, the whole part of which is the number of days since December 30, 1899, and the fractional part of which is the fraction of a day.
    BSTR = 8  # A pointer to a BSTR, which is a null-terminated character string in which the string length is stored with the string.
    IDISPATCH = 9  # Indicates a pointer to an IDispatch interface on an OLE object.
    ERROR_CODE = 10  # Indicates a 32-bit error code.
    BOOL = 11  # Indicates a Boolean value.
    VARIANT = 12  # Indicates an Automation variant.
    IUNKNOWN = 13  # Indicates a pointer to an IUnknown interface on an OLE object.
    DECIMAL = 14  # Indicates an exact numeric value with a fixed precision and scale. The scale is between 0 and 28.
    GUID = 72  # Indicates a GUID.
    BYTES = 128  # Indicates a binary value.
    STRING = 129  # Indicates a string value.
    WSTR = 130  # Indicates a null-terminated Unicode character string.
    NUMERIC = 131  # Indicates an exact numeric value with a fixed precision and scale. The scale is between 0 and 38.
    UDT = 132  # Indicates a user-defined variable.
    DATE = 133  # Indicates a date value (yyyymmdd).
    TIME = 134  # Indicates a time value (hhmmss).
    DATETIME = 135  # Indicates a date-time stamp (yyyymmddhhmmss plus a fraction in billionths).
    HCHAPTER = 136  # Indicates a four-byte chapter value used to identify rows in a child rowset.


class TimeLevels(Enum):
    """Breaks down the various time levels supported in both AtScale and ansi sql"""

    def __new__(cls, value, timestep, sql_name):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.index = value
        obj.timestep = timestep
        obj.sql_name = sql_name
        return obj

    # Only handling AtScale time levels that are also in ANSI SQL and are date_trunc
    # compatible right now; trying to be as generic as possible.
    Year = 0, TimeSteps.TimeYears, "year"
    Quarter = 1, TimeSteps.TimeQuarters, "quarter"
    Month = 2, TimeSteps.TimeMonths, "month"
    Week = (
        3,
        TimeSteps.TimeWeeks,
        "week",
    )  # this one acts weird with date_trunc, so using date_part
    Day = 4, TimeSteps.TimeDays, "day"
    Hour = 5, TimeSteps.TimeHours, "hour"
    Minute = 6, TimeSteps.TimeMinutes, "minute"
    Second = 7, TimeSteps.TimeSeconds, "second"

    def get_sql_expression(
        self,
        col: str,
        dbconn,
    ):
        if (
            self.sql_name == "day"
            or self.sql_name == "hour"
            or self.sql_name == "minute"
            or self.sql_name == "second"
        ):
            return dbconn._sql_expression_day_or_less(self.sql_name, column_name=col)
        else:
            return dbconn._sql_expression_week_or_more(self.sql_name, column_name=col)


class PlatformType(Enum):
    """PlatformTypes describe a type of supported data warehouse"""

    from atscale.db.connections import (
        BigQuery,
        Databricks,
        Iris,
        Postgres,
        Snowflake,
    )
    from atscale.db.sql_connection import SQLConnection

    def __new__(
        cls,
        dbconn_str: str,
        dbconn: SQLConnection = None,
    ):
        obj = object.__new__(cls)
        obj._value_ = dbconn_str
        obj.dbconn = dbconn
        return obj

    SNOWFLAKE = (Snowflake.platform_type_str, Snowflake)
    GBQ = (BigQuery.platform_type_str, BigQuery)
    DATABRICKS = (Databricks.platform_type_str, Databricks)
    IRIS = (Iris.platform_type_str, Iris)
    POSTGRES = (Postgres.platform_type_str, Postgres)


class RequestType(Enum):
    """Used for specifying type of http request"""

    GET = "GET"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class CheckFeaturesErrMsg(Enum):
    """Used for specifying the sort of error message to be displayed via _check_features"""

    ALL = ("Feature", "All")
    CATEGORICAL = ("Categorical feature", "Categorical")
    NUMERIC = ("Numeric feature", "Numeric")
    HIERARCHY = ("Hierarchy", "Hierarchy")

    def get_errmsg(self) -> str:
        """Renders a _check_features error message according to the feature list we're checking
           against

        Returns:
            str: The error message string.
        """
        return (
            f"The requested {self.value[0].lower()}(s) was/were not found: " + "{}"
        )  # fstring broken up such that bracket is preserved for downstream formatting


class FileType(Enum):
    """Used for specifying a file type as a function parameter, e.g. when verifying that a file path
    leads to a certain file type
    """

    YAML = ".yaml"
    YML = ".yml"


class SemanticObjectTypes(Enum):
    """Has each valid semantic object type and maps it to the string representation"""

    AGGREGATE = "aggregate"
    ALIAS = "alias"
    ALTERNATE = "alternate"
    ATTRIBUTE_REFERENCE = "attribute_reference"
    CALCULATION = "metric_calc"
    CALCULATION_GROUP = "calculation_group"
    CALCULATED_MEMBER = "calculated_member"
    CATALOG = "catalog"
    COLUMN = "column"
    CONNECTION = "connection"
    DATASET = "dataset"
    DATASET_PROPERTIES = "dataset_properties"
    DIALECT = "dialect"
    DRILLTHROUGH = "drillthrough"
    DIMENSION = "dimension"
    DIMENSION_RELATIONSHIP = "dimension_relationship"
    DIMENSION_RELATIONSHIP_REFERENCE = "dimension_relationship_reference"
    FACT_RELATIONSHIP_REFERENCE = "fact_relationship_reference"
    INCREMENTAL = "incremental"
    HIERARCHY = "hierarchy"
    LEVEL = "level"
    LEVEL_ATTRIBUTE = "level_attribute"
    MAP = "map"
    METRIC = "metric"
    METRICAL = "metrical"
    METRIC_REFERENCE = "metric_reference"
    METRICAL_ATTRIBUTE = "metrical_attribute"
    MODEL = "model"
    MODEL_RELATIONSHIP = "model_relationship"
    OVERRIDES = "overrides"
    PARALLEL_PERIOD = "parallel_period"
    PARTITION = "partition"
    PERSPECTIVE = "perspective"
    PERSPECTIVE_DIMENSION = "perspective_dimension"
    PERSPECTIVE_HIERARCHY = "perspective_hierarchy"
    PACKAGE = "package"
    SECONDARY_ATTRIBUTE = "secondary_attribute"
    SHARED_DEGENERATE_COLUMN = "shared_degenerate_column"
    SUB_PACKAGE = "sub_package"


class HierarchyTypes(Enum):
    """Represents the types of hierarchy a user can house within a dimension"""

    STANDARD = "standard"
    TIME = "time"


class PartitionTypes(Enum):
    """Represents the types of partitions a user can house within a model"""

    KEY = "key"
    NAME = "name"
    NAME_KEY = "name+key"


class RelationshipTypes(Enum):
    """Represents the types of partitions a user can house within a model"""

    SNOWFLAKE = "snowflake"
    EMBEDDED = "embedded"
