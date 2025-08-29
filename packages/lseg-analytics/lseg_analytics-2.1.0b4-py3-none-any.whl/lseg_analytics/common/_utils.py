"""Initial space for no any utility without defined topic/submodule"""

import functools
import inspect
import typing
from datetime import date
from itertools import islice

from lseg_analytics import _feature_flags as fflags

if typing.TYPE_CHECKING:
    from lseg_analytics_basic_client.models import ServiceErrorResponse


def is_date_annotation(annotation) -> bool:
    """Is typing annotation a date, optional date, or union with date?"""
    if typing.get_origin(annotation) is typing.Union:
        return date in typing.get_args(annotation)

    return annotation == date


def parse_incoming_dates(func: typing.Callable):
    """If function or method has date annotated variables - accept also ISO date strings

    ISO strings will be converted to dates.
    Warning: Typing annotations of the processed function stays the same.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args = list(args)
        params = inspect.signature(func).parameters
        for index, (name, param) in enumerate(islice(params.items(), len(args))):
            if is_date_annotation(param.annotation) and isinstance(args[index], str):
                args[index] = date.fromisoformat(args[index])
        for name, value in kwargs.items():
            # Exclude "private" parameters
            if name.startswith("_"):
                continue
            if is_date_annotation(params[name].annotation) and isinstance(value, str):
                kwargs[name] = date.fromisoformat(value)
        return func(*args, **kwargs)

    return wrapper


def _repr_full_name(space, name, joined_prefix=False):
    return (
        ("space.name=" if joined_prefix else "") + f"'{space}.{name}'"
        if fflags.REPR_SHOW_JOINED_SPACE_NAME
        else f"space={space!r} name={name!r}"
    )


def _at_id_string(obj):
    return f" at {hex(id(obj))}"


def main_object_repr(obj):
    """Generate representation for main API object"""

    cal_id = obj.id
    name = obj.__class__.__name__

    full_name = _repr_full_name(obj.location.space, obj.location.name)
    _id = _at_id_string(obj) if fflags.REPR_SHOW_ID_HEX else ""
    saved_status = ""

    if fflags.REPR_SHOW_ON_SERVER_STATUS:
        saved_status = "unsaved"

        if cal_id is not None:
            saved_prefix = ""
            cal_id_str = cal_id[:8] + "‥" if fflags.REPR_SHORTEN_SERVER_ID else cal_id
            saved_status = saved_prefix + cal_id_str

        saved_status = " " + saved_status
    return f"<{name} {full_name}{saved_status}{_id}>"
