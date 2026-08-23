type ValuePair = tuple[float, str]


def scale_minute(value: float) -> ValuePair:
    return (value / 60, "min")


def scale_hour(value: float) -> ValuePair:
    return (value / 3600, "hour")


def scale_distance(value: float) -> ValuePair:
    return (value / 1000, "km")


def scale_metre(value: float) -> ValuePair:
    return (value, "metre")


def scale_steps(value: float) -> ValuePair:
    return (value, "steps")


def scale_streak(value: float) -> ValuePair:
    return (value, "days")
