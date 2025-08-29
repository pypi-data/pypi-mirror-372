from typing import List, Union

from lseg_analytics.market_data.fx_forward_curves import FxOutrightCurvePoint
from lseg_analytics.reference_data.calendars import Holiday

__all__ = ["to_rows"]


def _plain_curve_point(point: FxOutrightCurvePoint):
    return {
        "tenor": point.tenor,
        "start_date": point.start_date,
        "end_date": point.end_date,
        "outright.bid": point.outright.bid,
        "outright.ask": point.outright.ask,
        "outright.mid": point.outright.mid,
    }


def _plain_holiday_output(output: Holiday):
    for oname in output.names:
        yield {
            "date": output.date,
            "name": oname.name,
            "calendars": oname.calendars,
            "countries": oname.countries,
        }


def to_rows(items: List[Union[FxOutrightCurvePoint, Holiday]]) -> List[dict]:
    """Convert list of FxForwardCurvePoint or HolidayOutput objects to list of dicts"""

    if isinstance(items, list):
        if not items:
            return []
        if isinstance(items[0], FxOutrightCurvePoint):
            return [_plain_curve_point(point) for point in items]
        elif isinstance(items[0], Holiday):
            result = []
            for item in items:
                result.extend(_plain_holiday_output(item))
            return result
    raise ValueError("Argument is not supported")
