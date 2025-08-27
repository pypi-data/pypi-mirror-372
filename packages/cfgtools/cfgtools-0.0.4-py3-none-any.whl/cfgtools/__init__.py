"""
# cfgtools
Provides tools for managing config files.

## Usage
### Save to a config file

```py
>>> import cfgtools
>>> cfg = cfgtools.config({"foo": "bar", "this": ["is", "an", "example"]})
>>> cfg.save("test.cfg", "yaml") # or: cfg.to_yaml("test.cfg")
```
If not specifeid, the format of the file will be automatically detected according to the
file suffix. Valid formats include `ini`, `json`, `yaml`, `pickle`, etc. For example:
```py
>>> cfg.save("test.yaml") # a yaml file is created
>>> cfg.save("test.pkl") # a pickle file is created
>>> cfg.save("unspecified.cfg") # by default a json file is created
```

### Read from a config file
```py
>>> cfgtools.read("test.cfg")
cfgtools.config({'foo': 'bar', 'this': ['is', 'an', 'example']})
```
The encoding and format of the file will be automatically detected if not specified.

## See Also
### Github repository
* https://github.com/Chitaoji/cfgtools/

### PyPI project
* https://pypi.org/project/cfgtools/

## License
This project falls under the BSD 3-Clause License.

"""

import lazyr

lazyr.VERBOSE = 0
lazyr.register("yaml")
lazyr.register(".test_case")

# pylint: disable=wrong-import-position
from . import core, iowrapper, reader, test_case, tpl
from .__version__ import __version__
from .core import *
from .iowrapper import *
from .reader import *
from .tpl import *

__all__: list[str] = ["test_case"]
__all__.extend(core.__all__)
__all__.extend(iowrapper.__all__)
__all__.extend(reader.__all__)
__all__.extend(tpl.__all__)
