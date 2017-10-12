# har-extractor

## Overview

Extractor for [`HAR`](https://dvcs.w3.org/hg/webperf/raw-file/tip/specs/HAR/Overview.html), HTTP Archive format.

## Requirements

- [`Python 3`](https://www.python.org/)

### Optional

- [`YAJL 2`](https://lloyd.github.io/yajl/)
- [`CFFI`](https://pypi.python.org/pypi/cffi)

## Installation

```
python setup.py install
```

```
pip install har-extractor
```

## Usage

```
usage: har-extractor [-h] [-v] [-l] [-o DIRECTORY] FILE

positional arguments:
  FILE                  HAR file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         list extracted files
  -l, --list            list the contents of input files
  -o DIRECTORY, --output-directory DIRECTORY
                        set output directory (default: ./<filename>.d)
```

## Testing

```
python setup.py test
```

```
coverage run --include har_extractor.py setup.py test
```

## Licenses

* [`har-extractor`](https://github.com/dead-beef/har-extractor/blob/master/LICENSE)
