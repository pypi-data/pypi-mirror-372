"""
Contains typing classes.

NOTE: this module is not intended to be imported at runtime.

"""

from typing import TYPE_CHECKING, Callable, Literal

import loggings

from .tpl import ConfigTemplate, Flag

if TYPE_CHECKING:
    from .iowrapper import ConfigIOWrapper

loggings.warning("this module is not intended to be imported at runtime")

BasicObj = str | int | float | bool | None | type | Callable | Flag
UnwrappedDataObj = (
    dict[BasicObj, "UnwrappedDataObj"] | list["UnwrappedDataObj"] | BasicObj
)
DataObj = dict[BasicObj, "DataObj"] | list["DataObj"] | BasicObj | ConfigTemplate
ConfigFileFormat = Literal[
    "yaml", "yml", "pickle", "pkl", "json", "ini", "text", "txt", "bytes"
]
