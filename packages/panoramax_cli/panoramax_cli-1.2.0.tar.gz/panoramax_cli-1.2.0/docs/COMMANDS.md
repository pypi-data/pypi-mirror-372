# `panoramax_cli`

Panoramax command-line client (v1.2.0)

**Usage**:

```console
$ panoramax_cli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`: Show Panoramax command-line client version and exit
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `upload`: Uploads some files.
* `check-sequences`: Checks pictures and sequences.
* `download`: Downloads one or many sequences.
* `transfer`: Transfer one or many sequences.
* `upload-status`: Status of one or many Upload Sets.
* `login`: Authenticate to the given instance.

## `panoramax_cli upload`

Uploads some files.

Upload some files to a Panoramax instance. The files will be associated to one or many sequences.

**Usage**:

```console
$ panoramax_cli upload [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Local path to your sequence folder  [required]

**Options**:

* `--api-url TEXT`: Panoramax endpoint URL  [required]
* `--wait / --no-wait`: Wait for all pictures to be ready  [default: no-wait]
* `--is-blurred / --is-not-blurred`: Define if sequence is already blurred or not  [default: is-not-blurred]
* `--title TEXT`: Collection title. If not provided, the title will be the directory name.
* `--token TEXT`: Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.
* `--sort-method [filename-asc|filename-desc|time-asc|time-desc]`: Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.  [default: time-asc]
* `--split-distance INTEGER`: Maximum distance between two pictures to be considered in the same sequence (in meters). If not provided, the instance&#x27;s default value will be used. Splitting can be disabled entirely with --no-split.
* `--split-time INTEGER`: Maximum time interval between two pictures to be considered in the same sequence (in seconds). If not provided, the instance&#x27;s default value will be used. Splitting can be disabled entirely with --no-split.
* `--no-split / --split`: If True, all pictures of this upload will be grouped in the same sequence. Is incompatible with split_distance / split_time.  [default: split]
* `--duplicate-distance FLOAT`: Maximum distance between two pictures to be considered as duplicates (in meters). If not provided, the instance&#x27;s default value will be used. Deduplication can be disabled entirely with --no-deduplication.
* `--duplicate-rotation INTEGER`: Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees). If not provided, the instance&#x27;s default value will be used. Deduplication can be disabled entirely with --no-deduplication.
* `--no-deduplication / --deduplication`: If True, no duplication will be done. Is incompatible with duplicate_distance / duplicate_rotation.  [default: deduplication]
* `--relative-heading INTEGER`: The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture upload_sets, 0° is heading north). For example, use 90° if the camera was mounted on the vehicle facing right. If not set, the headings are either retreived using the pictures metadata or computed using the movement path if no metadata is set.
* `--picture-upload-timeout FLOAT`: Timeout time to receive the first byte of the response for each picture upload (in seconds)  [default: 60.0]
* `--parallel-uploads INTEGER`: Amount of pictures to send in parallel  [default: 1]
* `--merge-subfolders / --separate-subfolders`: Should subfolders be considered as independent sequences, or sent as a single upload set ?  [default: separate-subfolders]
* `--disable-duplicates-check / --enable-duplicates-check`: Disable locally checking for pictures duplicates (almost same time and coordinates).
Disabling this avoids long local processing (duplicates are checked on server-side), enabling avoids sending useless pictures to server.
Choose depending on if your Internet is faster than your hard drive.  [default: enable-duplicates-check]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.

## `panoramax_cli check-sequences`

Checks pictures and sequences.
This simulates processing done by the server to reflect sequences splits,
find pictures duplicates and missing metadata.
This runs in local, nothing is sent to the server.

**Usage**:

```console
$ panoramax_cli check-sequences [OPTIONS] PATH
```

**Arguments**:

* `PATH`: Local path to your sequence folder  [required]

**Options**:

* `--report-file PATH`: Output JSON file to save report result. No JSON saved by default.
* `--geojson-dir PATH`: Output GeoJSON in a given directory. Each sequence is a GeoJSON file with all its pictures. 
The duplicates are also outputed in a special duplicates.geojson file. No GeoJSON saved by default.
* `--sort-method [filename-asc|filename-desc|time-asc|time-desc]`: Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.  [default: time-asc]
* `--split-distance INTEGER`: Maximum distance between two pictures to be considered in the same sequence (in meters).  [default: 100]
* `--split-time INTEGER`: Maximum time interval between two pictures to be considered in the same sequence (in seconds).  [default: 300]
* `--no-split / --split`: If True, all pictures of this upload will be grouped in the same sequence. Is incompatible with split_distance / split_time.  [default: split]
* `--duplicate-distance FLOAT`: Maximum distance between two pictures to be considered as duplicates (in meters).  [default: 1]
* `--duplicate-rotation INTEGER`: Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).  [default: 60]
* `--no-deduplication / --deduplication`: If True, no duplication will be done. Is incompatible with duplicate_distance / duplicate_rotation.  [default: deduplication]
* `--merge-subfolders / --separate-subfolders`: Should subfolders be considered as independent sequences, or sent as a single upload set ?  [default: separate-subfolders]
* `--help`: Show this message and exit.

## `panoramax_cli download`

Downloads one or many sequences.

**Usage**:

```console
$ panoramax_cli download [OPTIONS]
```

**Options**:

* `--api-url TEXT`: Panoramax endpoint URL  [required]
* `--collection TEXT`: Collection ID. Either use --collection or --user depending on your needs.
* `--user TEXT`: User ID, to get all collections from this user. Either use --collection or --user depending on your needs. The special value &#x27;me&#x27; can be provided to get you own sequences, if you&#x27;re logged in.
* `--path PATH`: Folder where to store downloaded collections.  [default: .]
* `--picture-download-timeout FLOAT`: Timeout time to receive the first byte of the response for each picture upload (in seconds)  [default: 60.0]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while downloading. This should not be used unless you __really__ know what you are doing.  [default: enable-cert-check]
* `--file-name [original-name|id]`: Strategy used for naming your downloaded pictures. Either by &#x27;original-name&#x27; (by default) or by &#x27;id&#x27; in Panoramax server.  [default: original-name]
* `--token TEXT`: Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.
* `--external-metadata-dir-name PATH`: Name of the folder where to store Panoramax API responses corresponding to each picture. 
This folder will be created in the pictures folder (so you can use &#x27;.&#x27; to download pictures in the same folder as the pictures).
If not provided, the API responses will not be persisted.
* `--quality [sd|hd|thumb]`: Quality of the pictures to download. Choosing a lower quality will reduce the download time.  [default: hd]
* `--help`: Show this message and exit.

## `panoramax_cli transfer`

Transfer one or many sequences.
This command copy sequences from origin API to destination API.
Note that it doesn&#x27;t delete sequences on origin API.

**Usage**:

```console
$ panoramax_cli transfer [OPTIONS]
```

**Options**:

* `--from-api-url TEXT`: Origin Panoramax endpoint URL  [required]
* `--from-collection TEXT`: Collection ID to transfer. Either use --from-collection or --from-user depending on your needs.
* `--from-user TEXT`: User ID (technical ID, not user name), to transfer all collections from this user. Either use --from-collection or --from-user depending on your needs. The special value &#x27;me&#x27; can be provided to get you own sequences, if you&#x27;re logged in.
* `--from-token TEXT`: Token on origin Panoramax instance if required. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.
* `--to-api-url TEXT`: Destination Panoramax endpoint URL  [required]
* `--to-token TEXT`: Token on destination Panoramax instance if required. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.
* `--picture-request-timeout FLOAT`: Timeout for getting the first byte of the response for each picture upload/download (in seconds)  [default: 60.0]
* `--parallel-transfers INTEGER`: Amount of pictures to transfer in parallel  [default: 1]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while downloading. This should not be used unless you __really__ know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.

## `panoramax_cli upload-status`

Status of one or many Upload Sets.

**Usage**:

```console
$ panoramax_cli upload-status [OPTIONS] IDS...
```

**Arguments**:

* `IDS...`: One or many Upload Set IDs  [required]

**Options**:

* `--api-url TEXT`: Panoramax endpoint URL
* `--token TEXT`: Panoramax token if the panoramax instance needs it. If none is provided and the panoramax instance requires it, the token will be asked during run. Note: is is advised to wait for prompt without using this variable.
* `--wait / --no-wait`: Wait for all pictures to be ready  [default: no-wait]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.

## `panoramax_cli login`

Authenticate to the given instance.

This will generate credentials and ask the user to visit a page to associate those credentials to the user&#x27;s account.

The credentials will be stored in /home/a_user/.config/geovisio/config.toml

**Usage**:

```console
$ panoramax_cli login [OPTIONS]
```

**Options**:

* `--api-url TEXT`: Panoramax endpoint URL  [required]
* `--disable-cert-check / --enable-cert-check`: Disable SSL certificates checks while uploading. This should not be used unless you __really__ know what you are doing.  [default: enable-cert-check]
* `--help`: Show this message and exit.
