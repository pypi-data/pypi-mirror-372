# cfgtools
Provides tools for managing config files.

## Installation
```sh
$ pip install cfgtools
```

## Requirements
```txt
pyyaml
lazyr
Faker
htmlmaster
```

## Usage
### Save to a config file

```py
>>> import cfgtools
>>> cfg = cfgtools.config({"foo": "bar", "this": ["is", "an", "example"]})
>>> cfg.save("test.cfg", "yaml") # or: cfg.to_yaml("test.cfg")
```
If not specifeid, the format of the file will be automatically detected according to the file suffix. Valid formats include `ini`, `json`, `yaml`, `pickle`, etc. For example:
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

## History
### v0.0.4
* Fixed a bug in path resolution.

### v0.0.3
* Added reliance on `htmlmaster`.

### v0.0.2
* New method `ConfigIOWrapper.safematch()`.

### v0.0.1
* Initial release.