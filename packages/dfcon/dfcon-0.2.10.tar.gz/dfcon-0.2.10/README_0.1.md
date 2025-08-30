# dfcon : dataFileController
To make access to the database easier.

## Installation
```Bash
pip install dfcon
```

## Requirements
- Python 3.x

## Usage
### module import ( and bref description )
```python
from dfcon import Directory
from dfcon.path_filter import DircFilter, FileFilter
from dfcon.filters import Filter, TiledFilter, OverlapedFilter
```
#### Directory
`Directory` can create hierarchical instances follow the hierarchical structure of the actual directory.
```python
dirc = Directory(path="path/to/target").build_structure()
```

#### Filter
`Filter` is the callable class that extends Python's conditional expressions.\
This can determine if an object meets the condition.\
`Filter` is abstruct class, the programmer can create filter classes for any object or data.

#### OverlapedFilter
`OverlapedFilter` is compound filter consisting of a Filter joined by the AND operator.\
This is `Filter`'s subclass.
```python
filter1 = MyFilter()
filter2 = MyFilter()
...

filters: OverlapedFilter = Filter.overlap([filter1, filter2, ...])
```

#### TiledFilter
`TiledFilter` is compound filter consisting of a Filter joined by the OR operator.\
This is `Filter`'s subclass.
```python
filters: TiledFilter = Filter.tile([filter1, filter2, ...])
```

#### DircFilter
`DircFilter` makes a judgment about the directory of the file path.\
This is `Filter`'s subclass.
```python
dfilter = DircFilter().contained_path("abc")

if dfilter("./src/sample.py"): # False
    ...
if dfilter("./abc/sample.py"): # True
    ...
```
`DircFilter` class used in `Directory` and its some function's arguments.

#### FileFilter
`FileFilter` makes a judgment about the filename of the file path.\
This is `Filter`'s subclass.
```python
ffilter = (
    FileFilter()
    .include_extention(["py", "txt"])
    .exclude_extention(["c", "cpp"])
)

if ffilter("./src/sample.py"): # True
    ...
if ffilter("./abc/sample.txt"): # True
    ...
if ffilter("./abc/sample.c"): # False
    ...
if ffilter("./abc/sample.cpp"): # False
    ...
```
`FileFilter` class used in `Directory` and its some function's arguments.