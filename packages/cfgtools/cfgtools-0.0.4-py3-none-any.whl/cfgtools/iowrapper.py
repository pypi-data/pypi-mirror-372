"""
Contains the io wrapper: ConfigIOWrapper.

NOTE: this module is private. All functions and objects are available in the main
`cfgtools` namespace - use that instead.

"""

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Self

from htmlmaster import HTMLTreeMaker

from .saver import ConfigSaver
from .tpl import (
    RETURN,
    YIELD,
    ConfigTemplate,
    DictConfigTemplate,
    Flag,
    ListConfigTemplate,
)

if TYPE_CHECKING:
    from ._typing import ConfigFileFormat, DataObj

NoneType = type(None)

__all__ = ["FileFormatError"]


SUFFIX_MAPPING = {
    ".yaml": "yaml",
    ".yml": "yaml",
    ".pickle": "pickle",
    ".pkl": "pickle",
    ".json": "json",
    ".ini": "ini",
    ".txt": "text",
    ".bytes": "bytes",
}
FORMAT_MAPPING = {
    "yaml": "yaml",
    "yml": "yaml",
    "pickle": "pickle",
    "pkl": "pickle",
    "json": "json",
    "ini": "ini",
    "text": "text",
    "txt": "text",
    "bytes": "bytes",
}


class ConfigIOWrapper(ConfigTemplate, ConfigSaver):
    """
    A wrapper for reading and writing config files.

    Parameters
    ----------
    data : DataObj
        The config data to be wrapped.
    fileformat : ConfigFileFormat, optional
        File format, by default None.
    path : str | Path | None, optional
        File path, by default None.
    encoding : str | None, optional
        The name of the encoding used to decode or encode the file
        (if needed), by default None.

    Raises
    ------
    TypeError
        Raised if the config data has invalid type.

    """

    valid_types = str, int, float, bool, NoneType
    constructor = object
    sub_constructors = {
        dict: lambda: DictConfigIOWrapper,
        list: lambda: ListConfigIOWrapper,
    }

    def __init__(
        self,
        data: "DataObj",
        fileformat: "ConfigFileFormat | None" = None,
        /,
        path: str | Path | None = None,
        encoding: str | None = None,
    ) -> None:
        super().__init__(data)
        self.fileformat = fileformat
        self.overwrite_ok = True
        if path is None:
            self.path = None
        else:
            abs_path, cwd_path = (path := Path(path)).absolute(), path.cwd()
            if abs_path.is_relative_to(cwd_path):
                self.path = abs_path.relative_to(cwd_path).as_posix()
            else:
                self.path = abs_path.relative_to(path.home()).as_posix()
        self.encoding = encoding

    def __enter__(self) -> Self:
        if self.path is None:
            raise TypeError("no default file path, please run self.set_path() first")
        if not self.overwrite_ok:
            raise TypeError(
                "overwriting the original path is not allowed, please run "
                "self.unlock() first"
            )
        self.lock()
        return self

    def __exit__(self, *args) -> None:
        self.unlock()
        self.save()

    def __repr__(self) -> str:
        if len(flat := repr(self.unwrap())) <= self.get_max_line_width():
            s = flat
        else:
            s = self.repr()
        return f"cfgtools.config({s})"

    def _repr_mimebundle_(self, *_, **__) -> dict[str, str]:
        return {"text/html": self.to_html().make()}

    def to_html(self) -> HTMLTreeMaker:
        main_maker = super().to_html()
        main_maker.add(
            (
                f"format: {self.fileformat!r} | path: {self.path!r} "
                f"| encoding: {self.encoding!r}"
            ),
            "i",
        )
        return main_maker

    def set_path(self, path: str | Path) -> None:
        """Set the path."""
        if not self.overwrite_ok:
            raise TypeError(
                "set_path() is not allowed when the instance is locked, "
                "please run self.unlock() first"
            )
        self.path = path

    def lock(self) -> None:
        """Lock the original path so that it can not be overwritten."""
        self.overwrite_ok = False

    def unlock(self) -> None:
        """Unlock the original path so that it can be overwritten."""
        self.overwrite_ok = True

    def match(self, template: "DataObj", /) -> Self | None:
        if isinstance(template, ConfigIOWrapper):
            template = ConfigTemplate(template.unwrap())
        elif not isinstance(template, ConfigTemplate):
            template = ConfigTemplate(template)

        recorder = template.replace_flags()
        unwrapped = template.unwrap_top_level()

        if isinstance(unwrapped, (dict, list)):
            return None
        if isinstance(unwrapped, type):
            if isinstance(self.unwrap_top_level(), unwrapped):
                return self.copy()
        elif isinstance(unwrapped, Callable):
            if unwrapped(self):
                return self.copy()
        elif self.unwrap_top_level() == unwrapped:
            return self.copy()

        if recorder:
            return recorder["RETURN"]
        return None

    def fullmatch(self, template: "DataObj", /) -> Self | None:
        if isinstance(template, ConfigIOWrapper):
            template = ConfigTemplate(template.unwrap())
        elif not isinstance(template, ConfigTemplate):
            template = ConfigTemplate(template)

        recorder = template.replace_flags()

        if (
            matched := self.match(template)
        ) is not None and matched.unwrap() == self.unwrap():
            if recorder:
                if "RETURN" in recorder:
                    return ConfigIOWrapper(recorder["RETURN"])
                if "YIELD" in recorder:
                    return ConfigIOWrapper(recorder["YIELD"])
            return matched
        return None

    def safematch(self, template: "DataObj", /) -> Self | None:
        if isinstance(template, ConfigIOWrapper):
            template = ConfigTemplate(template.unwrap())
        elif not isinstance(template, ConfigTemplate):
            template = ConfigTemplate(template)

        if template.has_flag(RETURN):
            raise ValueError("'RETURN' tags are not supported in safematch()")
        if template.has_flag(YIELD):
            raise ValueError("'YIELD' tags are not supported in safematch()")

        template.replace_flags()
        return template.fill(ConfigIOWrapper, self)

    def search(self, template: "DataObj", /) -> Self | None:
        return self.match(template)

    def has_flag(self, flag: Flag, /) -> bool:
        raise TypeError("method has_flag() is available only on templates")

    def replace_flags(
        self, recorder: dict[str, "DataObj"] | None = None, /
    ) -> dict[str, "DataObj"]:
        raise TypeError("method replace_flags() is available only on templates")

    def save(
        self,
        path: str | Path | None = None,
        fileformat: "ConfigFileFormat | None" = None,
        /,
        encoding: str | None = None,
    ) -> None:
        """
        Save the config.

        Parameters
        ----------
        path : str | Path | None, optional
            File path, by default None. If not specified, use `self.path`
            instead.
        fileformat : ConfigFileFormat | None, optional
            File format to save, by default None. If not specified, the
            file format will be automatically decided.
        encoding : str | None, optional
            The name of the encoding used to decode or encode the file
            (if needed), by default None. If not specified, use
            `self.encoding` instead.

        Raises
        ------
        ValueError
            Raised if both `path` and `self.path` are None.
        FileFormatError
            Raised if the file format is not supported.
        TypeError
            Raised if `self.overwrite_ok` is False.

        """
        if path is None:
            if self.path is None:
                raise ValueError(
                    "no default file path, please specify the path or run "
                    "self.set_path() first"
                )
            if not self.overwrite_ok:
                raise TypeError(
                    "overwriting the original path is not allowed, please run "
                    "self.unlock() first"
                )
            path = self.path
        if fileformat is None:
            if (suffix := Path(path).suffix) in SUFFIX_MAPPING:
                fileformat = SUFFIX_MAPPING[suffix]
            else:
                fileformat = "json" if self.fileformat is None else self.fileformat
        encoding = self.encoding if encoding is None else encoding
        if fileformat in FORMAT_MAPPING:
            super().save(path, FORMAT_MAPPING[fileformat], encoding=encoding)
        else:
            raise FileFormatError(f"unsupported config file format: {fileformat!r}")


class DictConfigIOWrapper(ConfigIOWrapper, DictConfigTemplate):
    """A wrapper for reading and writing config files."""

    constructor = ConfigIOWrapper
    sub_constructors = {}

    def match(self, template: "DataObj", /) -> Self | None:
        if isinstance(template, ConfigIOWrapper):
            template = ConfigTemplate(template.unwrap())
        elif not isinstance(template, ConfigTemplate):
            template = ConfigTemplate(template)

        recorder = template.replace_flags()
        unwrapped = template.unwrap_top_level()

        if matched := super().match(unwrapped):
            return matched
        if not isinstance(unwrapped, dict):
            return None

        new_data = {}
        for kt, vt in unwrapped.items():
            for k, v in self.items():
                if self.constructor(k).match(kt) and (matched := v.match(vt)):
                    new_data[k] = matched
                    break
            else:
                return None

        if recorder:
            if "RETURN" in recorder:
                return self.constructor(recorder["RETURN"])
            if "YIELD" in recorder:
                return self.constructor(recorder["YIELD"])
        return self.constructor(new_data)

    def search(self, template: "DataObj", /) -> Self | None:
        if matched := self.match(template):
            return matched
        for v in self.values():
            if searched := v.search(template):
                return searched
        return None


class ListConfigIOWrapper(ConfigIOWrapper, ListConfigTemplate):
    """A wrapper for reading and writing config files."""

    constructor = ConfigIOWrapper
    sub_constructors = {}

    def match(self, template: "DataObj", /) -> Self | None:
        if isinstance(template, ConfigIOWrapper):
            template = ConfigTemplate(template.unwrap())
        elif not isinstance(template, ConfigTemplate):
            template = ConfigTemplate(template)

        recorder = template.replace_flags()
        unwrapped = template.unwrap_top_level()

        if matched := super().match(unwrapped):
            return matched
        if not isinstance(unwrapped, list):
            return None

        new_data = []
        for xt in unwrapped:
            for x in self:
                if matched := x.match(xt):
                    new_data.append(matched)
                    break
            else:
                return None

        if recorder:
            if "RETURN" in recorder:
                return self.constructor(recorder["RETURN"])
            if "YIELD" in recorder:
                return self.constructor(recorder["YIELD"])
        return self.constructor(new_data)

    def search(self, template: "DataObj", /) -> Self | None:
        if matched := self.match(template):
            return matched
        for x in self:
            if searched := x.search(template):
                return searched
        return None


class FileFormatError(Exception):
    """Raised if the file format is not supported."""
