# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-08-27

### Changed

- Updated the duplicates detection, now detecting non consecutive duplicates. Also consider a picture a capture duplicate if there is less than 60° heading between a nearby picture (was 30°).
- Now spliting and merging default value uses the instance's default configuration (The previous default value was spliting in sequence if pictures are more than 1m appart and deleting capture duplicates if pictures were less than 1m appart (and 60° rotation angle for non 360° pictures)).
- The cli now have a `--no-deduplication` parameter to disable the deduplication feature and a `--no-split` parameter to disable the spliting in several sequences feature.
- The cli now always tells the API not to do deduplication, since it has either already been done by the CLI or it has been deactivated.

### Added 

- A geojson export in check-sequence. In a given directory, will create 1 geojson file per sequence, and one for the duplicates. Can be handy for debug.

## [1.1.8] - 2025-08-25

### Added

- Support `--relative-heading` parameter to `upload` command, to set the relative heading of the camera when uploading pictures.

### Changed

- Improved doc for PyPI updates from older Geovisio CLI.

## [1.1.7] - 2025-04-14

### Changed

- Update all required libraries (especially [geopic-tag-reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) and its [h3-py](https://github.com/uber/h3-py) dependency) to avoid an installation issue on Windows.

## [1.1.6] - 2025-02-25

### Fixed

- Pyinstaller build (Gitlab releases for Windows & Linux) was lacking `cameras.csv` file from Tag Reader, making uploads not working properly.

## [1.1.5] - 2025-02-10

### Changed

- Update dependencies, and especially the `geopic-tag-reader` library that improves the dupplicates detection ([v1.4.2](https://gitlab.com/panoramax/server/geo-picture-tag-reader/-/tags/1.4.2)).

## [1.1.4] - 2025-02-03

### Fixed

- The `check-sequences` command was not properly reporting duplicate pictures in JSON file.

### Added

- Display detailed error when available. It will especially be usefull for instances that require a term-or-service acceptance before upload.

## [1.1.3] - 2024-11-28

### Fixed

- If no title was set at upload, and folder name contained dots, the title generated from folder name was truncated (removed last dot and all following characters).
- As CLI folder naming scheme for downloaded sequences changed, integration tests were not expecting new names.

## [1.1.2] - 2024-11-25

### Added

- In command `check-sequences`, warnings raised by the _Tag Reader_ are now shown.

## [1.1.1] - 2024-10-22

### Changed

- Bump some dependencies and especially the geo-picture-tag-reader to the [newest version](https://gitlab.com/panoramax/server/geo-picture-tag-reader/-/tags/1.3.2), fixing the CLI for python 3.13.

### Added

- A retry mechanism for all http calls.

## [1.1.0] - 2024-10-15

### Changed

- Add more output when reading a csv with external metadata, and only read `panoramax.csv` files. 
- Replace library `requests` by [httpx](https://www.python-httpx.org/) to fix a memory leak.

### Fixed

- Fix authentication when transfering pictures between two panoramax instances.

## [1.0.0] - 2024-10-09

⚠️ Breaking change: rename executable from `geovisio` to `panoramax_cli`. Also moved pypi package from `geovisio_cli` to `panoramax_cli`.

### Added

- A new `download` command to download all pictures from one or many sequences.
- A new `check-sequences` command allows to check locally if your pictures are valid before upload, and how they will be split into sequences by API.
- A new `transfer` command allows to entirely copy one or all collections of an user from a GeoVisio instance to another.

### Changed

- Update doc and links to match the Gitlab renaming of GeoVisio organization into Panoramax.
- __Breaking change__: we only use now the _Upload Set_ API routes for managing uploads, instead of previously pushing on _Collections_ routes. A lot of internal rework has been done, bringing new features and changes:
  - `upload` command has a new parameter `--parallel-uploads` for sending many pictures in parallel 🚀
  - `upload-status` command replaces `collection-status` to reflect that you need __Upload Set ID__ to follow API processing progress.
  - `_geovisio.toml` has been removed, all information about upload status is synced with API at start.
  - `test-process` command has been removed as no TOML file is generated anymore. You may use `check-sequences` instead.
- ⚠️ Breaking change: the minimal required Python version is now 3.9.
- Update Geopic Tag Reader to 1.3.0, improving management of timestamps.
- while developping with an external Panoramax API for tests, provide the parameter `external-panoramax-url` instead of `external-geovisio-url`.

## [0.3.14] - 2024-10-09

### Changed

- Add deprecation warning, it's the last version published as `geovisio_cli`, the one to use now is `panoramax_cli`.

## [0.3.13] - 2024-04-30

### Changed

- Higher timeout for `collection-status` command (and collection checks on retry after failure).

## [0.3.12] - 2024-04-18

### Changed

- Updated Geopic Tag Reader to 1.1.0 to improve handling of timezones.

## [0.3.11] - 2024-04-09

### Added

- Folder name appears in error output [https://gitlab.com/panoramax/clients/cli/-/issues/38](#38)

### Fixed

- Automatic title associated to a sequence works also when uploading from a directory itself (`geovisio upload .`) [https://gitlab.com/panoramax/clients/cli/-/issues/22](#22)
- A check to avoid empty `geovisio_status` API call to block upload.


## [0.3.10] - 2024-04-08

### Added

- Automatic retries on HTTP calls, which makes a smoother experience if server drops some calls.

### Changed

- Checks for duplicated pictures better handles many following pictures under distance (previously check was done on each single picture, now done using last valid picture).
- Connection timeout augmented to 15 seconds.

### Fixed

- Sorting by filename on sequences mixing numeric and non-numeric notation was failing.


## [0.3.9] - 2024-03-15

### Changed

- Update [geo-picture-tag-reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) to [1.0.5 version](https://gitlab.com/panoramax/server/geo-picture-tag-reader/-/tags/1.0.5).


## [0.3.8] - 2023-12-20

### Changed

- Update [geo-picture-tag-reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) to [1.0.3 version](https://gitlab.com/panoramax/server/geo-picture-tag-reader/-/tags/1.0.3).

## [0.3.7] - 2023-11-24

### Changed
- Better display of error messages details (useful to know what is wrong with pictures metadata).


## [0.3.6] - 2023-11-17

### Changed
- Update Geopic Tag Reader to 1.0.2 to fix fractions reading issue.


## [0.3.5] - 2023-11-17

### Changed
- Update Geopic Tag Reader to 1.0.1 to fix `DateTimeOriginal` decimal seconds reading issue.


## [0.3.4] - 2023-11-14

### Fixed
- Some read/write issues on `_geovisio.toml` file with binary EXIF metadata (due to the TOML library which was used, switched to `tomli` instead).


## [0.3.3] - 2023-10-30

### Added
- Metadata for pictures can be read from an external CSV file. You can define there main metadata (coordinates, capture date) as well as any custom EXIF/XMP tag.
- Update Geopic Tag Reader to 1.0.0 to benefit from extended EXIF support.
- New parameters `--duplicate-distance` and `--duplicate-rotation` allow to remove duplicate pictures based on distance and heading delta.

### Changed
- Loosen requirements version, to make it easier to use this as a dependency.


## [0.3.2] - 2023-09-08

### Changed
- Updated GeoPic Tag Reader to 0.4.1 to embed more checks on pictures GPS coordinates.

### Fixed
- Added a timeout handling on CLI version check at startup, in case PyPI takes too long to answer.


## [0.3.1] - 2023-08-03

### Added
- Add `--picture-upload-timeout` to upload, to change the timeout of a picture upload
- Add `--disable-cert-check` to all commands, to disable ssl certificate check. This should not be used, unless if you -really- know what you are doing.

## [0.3.0] - 2023-07-20

### Added
- CLI now supports splitting a sequence into multiple sequences when distance or time exceeds a given delta. These can be set on upload with `--split-time` or `--split-distance` parameters.


## [0.2.3] - 2023-07-13

### Changed
- Support of Python >= 3.8

## [0.2.2] - 2023-06-26

### Fixes
- Add missing `packaging` dependency

## [0.2.1] - 2023-06-22

### Added
- A new parameter `--sort-method` allows user to choose how pictures should be sorted, either by their date/time or file name, in ascending or descending order. Default is now by date/time ascending (was previously by filename ascending).
- A new `--version` parameter to get the geovisio_cli version

### Changed
- A new warning is displayed on every command if the package version is not the latest

### Fixes
- Uploading twice the same sequence do not print any misleading errors

## [0.2.0] - 2023-05-24

### Added
- A new `--token` parameter to `geovisio upload` to provide a custom geovisio token for authentication.
- A new `geovisio login` command to login on a geovisio instance

### Changed
- If a geovisio instance has a mandatory login for upload, the upload will ask to register the computer in the user's account first, if the user has not done a `geovisio login` first

### Removed
- Giving a user/password to `geovisio upload` is deprecated, authentication should use a token.

## [0.1.0] - 2023-05-17

### Added
- A new `--title` parameter to `geovisio upload` and `geovisio test_process` to provide a title to the uploaded collection. If no title is given, it will default to the directory name.
- Broken uploads can now be recovered: if on a first upload try, some pictures fail, you can re-launch a second upload try by running the same `upload` command. The `_geovisio.toml` stores in a sequence folder which pictures were correctly sent, thus skip them on next try.

### Changed
- Command `test-process` generates a `_geovisio.toml` file in the sequence folder. This file can be edited before running command `upload` to change picture ordering.
- Increase timeout to geovisio and add better error when a timeout happen or when a connection is lost


## [0.0.5] - 2023-04-27

### Fixed
- Add a timeout to avoid `requests` module to hang forever if API is not responding


## [0.0.4] - 2023-04-14

### Changed
- Changed the `--path` option of the `geovisio upload` command to a positional argument since it seems more ergonomic. So now `geovisio upload --api-url <some_url> --path <some dir>` is replaced by `geovisio upload --api-url <some_url> <some dir>` (or `geovisio upload <some dir> --api-url <some_url>` since the parameters order is not relevant)
- Improve some error messages

## [0.0.3] - 2023-04-12

### Added
- A new `--is-blurred` flag is available on upload command to inform API that it doesn't need to blur pictures


## [0.0.2] - 2023-04-07

### Fixed
- Pictures were not sorted in alphabetical or numeric order
- Add a `--wait` flag to the upload command to wait for geovisio to have processed all pictures
- Add a `geovisio collection-status` command, to get the status of a collection


## [0.0.1] - 2023-03-14

### Added
- Basic scripts for uploading pictures to a GeoVisio API


[Unreleased]: https://gitlab.com/panoramax/clients/cli/-/compare/1.2.0...main
[1.2.0]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.8...1.2.0
[1.1.8]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.7...1.1.8
[1.1.7]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.6...1.1.7
[1.1.6]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.5...1.1.6
[1.1.5]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.4...1.1.5
[1.1.4]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.3...1.1.4
[1.1.3]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.2...1.1.3
[1.1.2]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.1...1.1.2
[1.1.1]: https://gitlab.com/panoramax/clients/cli/-/compare/1.1.0...1.1.1
[1.1.0]: https://gitlab.com/panoramax/clients/cli/-/compare/1.0.0...1.1.0
[1.0.0]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.14...1.0.0
[0.3.14]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.13...0.3.14
[0.3.13]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.12...0.3.13
[0.3.12]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.11...0.3.12
[0.3.11]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.10...0.3.11
[0.3.10]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.9...0.3.10
[0.3.9]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.8...0.3.9
[0.3.8]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.7...0.3.8
[0.3.7]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.6...0.3.7
[0.3.6]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.5...0.3.6
[0.3.5]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.4...0.3.5
[0.3.4]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.3...0.3.4
[0.3.3]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.2...0.3.3
[0.3.2]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.1...0.3.2
[0.3.1]: https://gitlab.com/panoramax/clients/cli/-/compare/0.3.0...0.3.1
[0.3.0]: https://gitlab.com/panoramax/clients/cli/-/compare/0.2.3...0.3.0
[0.2.3]: https://gitlab.com/panoramax/clients/cli/-/compare/0.2.2...0.2.3
[0.2.2]: https://gitlab.com/panoramax/clients/cli/-/compare/0.2.1...0.2.2
[0.2.1]: https://gitlab.com/panoramax/clients/cli/-/compare/0.2.0...0.2.1
[0.2.0]: https://gitlab.com/panoramax/clients/cli/-/compare/0.1.0...0.2.0
[0.1.0]: https://gitlab.com/panoramax/clients/cli/-/compare/0.0.5...0.1.0
[0.0.5]: https://gitlab.com/panoramax/clients/cli/-/compare/0.0.4...0.0.5
[0.0.4]: https://gitlab.com/panoramax/clients/cli/-/compare/0.0.3...0.0.4
[0.0.3]: https://gitlab.com/panoramax/clients/cli/-/compare/0.0.2...0.0.3
[0.0.2]: https://gitlab.com/panoramax/clients/cli/-/compare/0.0.1...0.0.2
[0.0.1]: https://gitlab.com/panoramax/clients/cli/-/commits/0.0.1
