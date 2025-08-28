from aenum import Enum

from atscale.base.parent_enums import TimeSteps_Parent, Aggs_Parent


class TimeSteps(TimeSteps_Parent):
    """Translates the time levels into usable step sizes."""

    Regular = 0, [0]
    TimeYears = 20, [1, 2]
    TimeHalfYears = 36, [1, 2]
    TimeTrimester = 4722, [1, 3]
    TimeQuarters = 68, [1, 4]
    TimeMonths = 132, [1, 3, 6, 12]
    TimeWeeks = 260, [1, 4]
    TimeDays = 516, [1, 7, 28]
    TimeHours = 772, [1, 12, 24]
    TimeMinutes = 1028, [1, 60]
    TimeSeconds = 2052, [1, 60]
    TimeUndefined = 4100, [0]


class Aggs(Aggs_Parent):
    """Holds constant string representations for the supported aggregation methods of numerical aggregate features
    SUM: Addition
    AVG: Average
    MAX: Maximum
    MIN: Mininum
    DISTINCT_COUNT: Distinct-Count (count of unique values)
    DISTINCT_COUNT_ESTIMATE: An estimate of the distinct count to save compute
    NON_DISTINCT_COUNT: Count of all values
    STDDEV_SAMP: standard deviation of the sample
    STDDEV_POP: population standard deviation
    VAR_SAMP: sample variance
    VAR_POP: population variance
    """

    SUM = "SUM", "Sum"
    AVG = "AVG", "Average"
    MAX = "MAX", "Max"
    MIN = "MIN", "Min"
    DISTINCT_COUNT = "DC", "Distinct Count"
    DISTINCT_COUNT_ESTIMATE = "DCE", "Distinct Count Estimate"
    NON_DISTINCT_COUNT = "NDC", "Non Distinct Count"
    STDDEV_SAMP = "STDDEV_SAMP", "Sample Standard Deviation"
    STDDEV_POP = "STDDEV_POP", "Population Standard Deviation"
    VAR_SAMP = "VAR_SAMP", "Sample Variance"
    VAR_POP = "VAR_POP", "Population Variance"


class TableExistsAction(Enum):
    """Potential actions to take if a table already exists when trying to write a dataframe to that database table.
    APPEND: Append content of the dataframe to existing data or table
    OVERWRITE: Overwrite existing data with the content of dataframe
    IGNORE: Ignore current write operation if data/ table already exists without any error. This is not valid for
        pandas dataframes
    ERROR: Throw an exception if data or table already exists
    """

    def __new__(cls, value, pandas_value):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.pandas_value = pandas_value
        return obj

    APPEND = "append", "append"
    OVERWRITE = "overwrite", "replace"
    IGNORE = "ignore", None
    ERROR = "error", "fail"


class FeatureType(Enum):
    """Used for specifying all features or only numerics or only categorical"""

    def __new__(
        cls,
        value,
        name_val,
    ):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.name_val = name_val
        return obj

    ALL = (0, "All")
    NUMERIC = (1, "Numeric")
    CATEGORICAL = (2, "Categorical")
