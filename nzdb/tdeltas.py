from datetime import timedelta
import delorean
import re

"""
calculate series of time intervals
"""


def parse_delta(interval: str) -> timedelta:
    """find the timedelta corresponding to the given string

    Args:
        interval (str): interval indicator (.eg., 1d 1h 3w)
    """
    delta = None
    pattern = r"(\d+)([hdw])"
    match = re.match(pattern, interval)
    if match:
        num, unit = match.group(1, 2)
        num = int(num)
        match unit:
            case "h":
                delta = timedelta(hours=num)
            case "d":
                delta = timedelta(days=num)
            case "w":
                delta = timedelta(weeks=num)
        return delta
    else:
        raise Exception("Error in parse_delta")


def calc_intervals(start: str, interval: str, nintvls: int):
    """calculate series of start/end datetime pairs, utc assumed

    Args:
        start (string): start time in form yyyy-mm-ddThh:mm:ss (z assumed)
        interval (string): interval indicator (e.g., 1d 1h 3m)
        nintvls (int): number of intervals
    """
    startde = delorean.parse(start, yearfirst=True, dayfirst=False)
    delta = parse_delta(interval)
    intervals = []
    s = startde.datetime
    for i in range(nintvls):
        e = s + delta
        intervals.append([s, e])
        s = e
    return intervals
