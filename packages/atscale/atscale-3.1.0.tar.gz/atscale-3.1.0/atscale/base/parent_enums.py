from aenum import Enum

from atscale.errors import atscale_errors


class TimeSteps_Parent(Enum):
    """Translates the time levels into usable step sizes."""

    def __new__(
        cls,
        value,
        steps,
    ):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.steps = steps
        return obj

    def _get_steps(self):
        if self.name == "Regular" or self.name == "TimeUndefined":
            return None
        else:
            return self.steps


class Aggs_Parent(Enum):
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

    def __new__(cls, key_name, visual_rep):
        obj = object.__new__(cls)
        obj._value_ = key_name
        obj._customer_representation = visual_rep
        return obj

    @property
    def _visual_rep(self):
        return self._customer_representation

    # UNUSED UNTIL THE DMV BUG IS SORTED
    # @classmethod
    # def from_properties(cls, property_dict):
    #     if property_dict is None:
    #         return ""
    #     type_section = property_dict.get("type", {})
    #     if "metric" in type_section:
    #         return cls[type_section["metric"]["default-aggregation"]]
    #     elif "count-distinct" in type_section:
    #         if type_section["count-distinct"]["approximate"]:
    #             return cls.DISTINCT_COUNT_ESTIMATE
    #         else:
    #             return cls.DISTINCT_COUNT
    #     elif "count-nonnull":
    #         return cls.NON_DISTINCT_COUNT

    @classmethod
    def _from_dmv_number(cls, number):
        num_to_value = {
            1: cls.SUM,
            5: cls.AVG,
            4: cls.MAX,
            3: cls.MIN,
            8: cls.DISTINCT_COUNT,
            1000: cls.DISTINCT_COUNT_ESTIMATE,  # dmv bug, comes back as 8
            2: cls.NON_DISTINCT_COUNT,
            7: cls.STDDEV_SAMP,
            333: cls.STDDEV_POP,  # dmv bug, comes back as 0
            0: cls.VAR_POP,
            6: cls.VAR_SAMP,
        }
        obj = num_to_value[number]
        return obj
