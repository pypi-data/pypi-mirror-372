"""
Setup the package.

To use the full functionality of this file, you must:

```sh
$ pip install pyyaml
$ pip install re-extensions
```
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from pathlib import Path
from typing import Any, Final

import yaml
from re_extensions import rsplit, word_wrap

here = Path(__file__).parent

# Load the package's meta-data from metadata.yml.
yml: dict[str, Any] = yaml.safe_load((here / "metadata.yml").read_text())
NAME: Final[str] = yml["NAME"]
SUMMARY: Final[str] = yml["SUMMARY"]
HOMEPAGE: Final[str] = yml["HOMEPAGE"]
REQUIRES: Final[list[str]] = yml["REQUIRES"]
SOURCE: str = yml["SOURCE"]
LICENSE = (here / "LICENSE").read_text().partition("\n")[0]

# Import the README and use it as the long-description.
readme_path = here / "README.md"
if readme_path.exists():
    long_description = "\n" + readme_path.read_text()
else:
    long_description = SUMMARY


def _readme2doc(
    readme: str,
    name: str = NAME,
    requires: list[str] = REQUIRES,
    homepage: str = HOMEPAGE,
    pkg_license: str = LICENSE,
) -> tuple[str, str]:
    doc, rd = "", ""
    for i, s in enumerate(rsplit("\n## ", readme)):
        head = re.search(" .*\n", s).group()[1:-1]
        if i == 0:
            s = re.sub("^\n# .*", f"\n# {name}", s)
        elif head == "Requirements":
            s = re.sub(
                "```txt.*```",
                "```txt\n" + "\n".join(requires) + "\n```",
                s,
                flags=re.DOTALL,
            )
        elif head == "Installation":
            s = re.sub(
                "```sh.*```", f"```sh\n$ pip install {name}\n```", s, flags=re.DOTALL
            )
        elif head == "See Also":
            pypipage = f"https://pypi.org/project/{name}/"
            s = re.sub(
                "### PyPI project\n.*",
                f"### PyPI project\n* {pypipage}",
                re.sub(
                    "### Github repository\n.*",
                    f"### Github repository\n* {homepage}",
                    s,
                ),
            )
        elif head == "License":
            s = f"\n## License\nThis project falls under the {pkg_license}.\n"

        rd += s
        if head not in {"Installation", "Requirements", "History"}:
            doc += s
    doc = re.sub("<!--html-->.*<!--/html-->", "", doc, flags=re.DOTALL)
    return word_wrap(doc, maximum=88) + "\n\n", rd


def _quote(readme: str) -> str:
    if "'''" in readme and '"""' in readme:
        raise ReadmeFormatError("Both \"\"\" and ''' are found in the README")
    if '"""' in readme:
        return f"'''{readme}'''"
    else:
        return f'"""{readme}"""'


class ReadmeFormatError(Exception):
    """Raised when the README has a wrong format."""


if __name__ == "__main__":
    # Import the __init__.py and change the module docstring.
    init_path = here / SOURCE / "__init__.py"
    module_file = init_path.read_text()
    new_doc, long_description = _readme2doc(long_description)
    module_file = re.sub(
        "^\"\"\".*\"\"\"|^'''.*'''|^", _quote(new_doc), module_file, flags=re.DOTALL
    )
    init_path.write_text(module_file)
    readme_path.write_text(long_description.strip())
