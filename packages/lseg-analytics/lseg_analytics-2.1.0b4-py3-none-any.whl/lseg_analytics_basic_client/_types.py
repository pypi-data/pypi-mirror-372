# coding=utf-8


from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import models as _models
JobStoreInputData = Union[
    "_models.PrepayDialsInput",
    "_models.UserCurve",
    "_models.UserVol",
    "_models.CMOModification",
    "_models.UserScenarioInput",
    "_models.DataTable",
    "_models.YBPortUserBond",
]
