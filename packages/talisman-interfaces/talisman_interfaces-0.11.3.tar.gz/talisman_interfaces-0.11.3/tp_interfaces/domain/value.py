import enum

from tdm.datamodel.values import DateTimeValue, DoubleValue, GeoPointValue, IntValue, LinkValue, StringValue, TimestampValue


class ValueTypes(enum.Enum):
    Date = DateTimeValue
    Double = DoubleValue
    Geo = GeoPointValue
    Int = IntValue
    Timestamp = TimestampValue
    Link = LinkValue
    String = StringValue

    @classmethod
    def get(cls, key: str, default_value=None):
        if key in cls.__members__.keys():
            return cls[key].value
        return default_value
