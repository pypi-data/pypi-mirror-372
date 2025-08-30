# Change Log
## [0.0.1] - 2023-01-30
### Added
- `Directory` class and its basic fuctions from @MTamon
- `Filter` class and its basic fuctions from @MTamon
- `OverlapedFilter` class and its basic fuctions from @MTamon
- `TiledFilter` class and its basic fuctions from @MTamon
- `DircFilter` class and its basic fuctions from @MTamon
- `FileFilter` class and its basic fuctions from @MTamon
- `EmpFilter` class and its \_\_call\_\_ fuctions from @MTamon

## [0.0.2] - 2023-01-30
### Fixed
- Some functions description typo fixed from @MTamon
- Module import method fixed for module classification from @MTamon

## [0.0.3] - 2023-01-30
### Added
- Some description added from @MTamon

## [0.0.4] - 2023-01-31
### Fixed
- Module import method fixed for module classification from @MTamon

## [0.0.5] - 2023-01-31
### Added
- Supported stability of `Directory`'s `get_file_path()` results from @MTamon

## [0.0.6] - 2023-05-30
### Added
- Supported fuction for changing Directory's name.

## [0.0.7] - 2023-05-30
### Fixed
- Change `update_dir_name()` return value: None -> self

## [0.0.8] - 2023-05-31
### Added
- Supported fuction for copying files in hierarchy.

## [0.0.9] - 2023-05-31
### Fixed
- Fixed sum bugs. (in Filter.overlap & Filter.tile)

## [0.0.10] - 2023-05-31
### Fixed
- Fixed sum bugs. (in Filter.overlap & Filter.tile)

## [0.0.11] - 2023-05-31
### Fixed
- Fixed `Directory.copy_files`. (for printer=None)

## [0.0.12] - 2023-05-31
### Added
- Supported tqdm for `copy_file()` & `copy_files()`.

## [0.0.13] - 2023-05-31
### Fixed
- Fixed `Directory.sub_incarnate()` (for directory filtering)

## [0.0.14] - 2023-06-01
### Fixed
- Fixed requirements.txt (tqdm)

## [0.0.15] - 2023-06-01
### Fixed
- Fixed DircFilter bug. (about valiable 'target')

## [0.0.16] - 2023-06-01
### Fixed
- Fixed FileFilter bug. (When `__call__()` called, target=Directory)

## [0.0.17] - 2023-10-30
### Fixed
- Fixed for pylance type check.

## [0.0.18] - 2023-11-05
### Added
- suport operator '&' @ filter

## [0.0.19] - 2023-11-05
### Fixed
- Fixed for Directory motion when `emp=True`

## [0.1.0] - 2023-11-29
### Add
- `filters` independents from me as `cmpfilter`.
- and `pip install cmpfilter` 

## [0.2.0] - 2023-12-01
### Fixed
- change directory.py for speed up.

## [0.2.1] - 2023-12-01
### Add
- Add empty argment in incarnate() to output empty directory for making new output site.

## [0.2.2] - 2023-12-01
### Add
- new README.md for version 0.2.1 ~.

## [0.2.3] - 2023-12-04
### Add
- add file-filter function start_with() & end_with()

## [0.2.4] - 2023-12-27
### Fix
- DircFilter._only_terminal_dirc judgement code.

## [0.2.5] - 2024-10-27
### Fix
- Dirctory.get_instance() code

## [0.2.6] - 2024-10-27
### Fix
- Dirctory.get_instance() code

## [0.2.7] - 2024-11-02
### Fix
- Dirctory.get_instance() code: activate filters

## [0.2.8] - 2025-01-24
### Fix
- filefilter: more kind summary & end_with/start_with() for behaving like the logical sum.

## [0.2.9] - 2025/01/24
### Fix
- fix bug in path_filter variable 'exist'

## [0.2.10] - 2025/08/29
### Add
- add get_child_instances() and return_generator flag in get_instances.

## [0.2.11] - 2025/08/30
### Fix
- fix bug in get_instances() about child_only flag