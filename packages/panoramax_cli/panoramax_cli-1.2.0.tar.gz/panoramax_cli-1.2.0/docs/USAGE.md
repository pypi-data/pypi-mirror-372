# Usage

## :material-upload: Upload pictures

The picture upload command is available under the `upload` subcommand:

```bash
panoramax_cli upload --help
```

If you want to upload pictures from a `my_sequence` directory to a Panoramax instance (running locally in this example), launch this command:

```bash
panoramax_cli upload --api-url https://my.panoramax.server/ ./my_sequence
```

You can also add a `--wait` flag to wait while the server processes all the pictures.

!!! note
	You can launch again the same command to recover a partial sequence import, for example if only some pictures failed to upload.

### :key: Authentication

If your Panoramax instance requires a login for the upload, the `upload` command will ask for a login on the instance by visiting a given url with a browser.

You can also login before hand with the command:

```bash
panoramax_cli login --api-url https://my.panoramax.server/
```

Both will store the credentials in a configuration file, located either in a [XDG](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) defined directory or in a user specific .config, in a subdirectory `geovisio/config.toml`.

If you do not want to use this, you can also provide an API token with the `--token` parameter.

## :material-microsoft-excel: External metadata

By default, picture metadata are read from EXIF tags of the image file. If they are not set, you can also use a CSV file. This file should be placed in the same directory as pictures, and should be named `panoramax.csv`.

The CSV file should contain all following columns:

Header | Type  | Mandatory ? | Description
-------|-------|-------------|-----------
file   | str   | Yes         | File name of the picture
lon    | float | No          | WGS84 longitude (for example 55.56 for Réunion Island)
lat    | float | No          | WGS84 latitude (for example -21.14 for Réunion Island)
capture_time|str| No         | Capture time of the picture, in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) (like `1985-04-12T23:20:50.52Z`). If no timezone is given, considered as local time (and thus the date + position would be used to localize it).
Exif.* | str   | No          | Any EXIF tag, with column name following [Exiv2](https://exiv2.org/metadata.html) scheme (example Exif.Image.Artist). You can create as many columns as necessary.
Xmp.*  | str   | No          | Any XMP tag, with column name following [Exiv2](https://exiv2.org/metadata.html) scheme (example Xmp.digiKam.TagsList). You can create as many columns as necessary.

All metadatas defined in the CSV are optional. If a metadata is not defined in CSV for a given image, Panoramax CLI will try to read it from picture EXIF metadata.

!!! note
	A Panoramax server [will always need some metadata to be present](https://docs.panoramax.fr/pictures-metadata/) (the GPS coordinates and the capture time), no matter where they are read from.

!!! tip
	If you want to manage finely your pictures metadata, we recommend using [Exiftool](https://exiftool.org/), which is a command-line utility for managing EXIF tags. For example, to add tags to all pictures in some directory:

	```bash
	exiftool -Artist='My Name' -ImageDescription='Some description' -overwrite_original /path/to/*.jpg
	```

	So in a broader process of managing pictures, you can first edit tags using Exiftool, then upload them with Panoramax CLI.

## :octicons-info-16: Upload status

Prints the status of an upload set.

```bash
panoramax_cli upload-status <some upload_set id> --api-url https://my.panoramax.server
```

You can also add a `--wait` flag to wait for all the pictures to be processed.

## :material-download: Download pictures

You can easily down pictures from a panoramax instance with the `download` subcommand.

You can download the pictures from a specific collection:

```bash
panoramax_cli download --api-url https://my.panoramax.server/ --collection "12345678-94c5-4c13-871f-0c82e24e3fc6" --path ./downloaded_pictures
```

or all the pictures of a user:

```bash
panoramax_cli download --api-url https://my.panoramax.server/ --user "12345678-94c5-4c13-871f-0c82e24e3fc6" --path ./downloaded_pictures
```

or your own pictures with the user id `me` (it will require a login):

```bash
panoramax_cli download --api-url https://my.panoramax.server/ --user me --path ./downloaded_pictures
```

## :material-sync: Transfer pictures

You can transfer pictures from one Panoramax instance to another with the `transfer` subcommand.

You can transfer a specific collection:

```bash
panoramax_cli transfer --from-api-url https://my.old.panoramax.server/ --to-api-url  https://my.new.shiny.panoramax.server/ --from-collection "12345678-94c5-4c13-871f-0c82e24e3fc6"
```

or all the pictures of a user:

```bash
panoramax_cli transfer --from-api-url https://my.old.panoramax.server/ --to-api-url  https://my.new.shiny.panoramax.server/ --user "12345678-94c5-4c13-871f-0c82e24e3fc6"
```

or your own pictures with the user id `me` (it will require a login):

```bash
panoramax_cli transfer --from-api-url https://my.old.panoramax.server/ --to-api-url  https://my.new.shiny.panoramax.server/ --user me
```
