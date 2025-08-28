from __future__ import annotations
from panoramax_cli.metadata import MetadataHandler, utils
from panoramax_cli.exception import CliException
from pathlib import Path
import csv
from geopic_tag_reader import reader
from typing import Dict, Optional, Tuple
from rich import print


def check(reader: csv.DictReader) -> bool:
    if not reader.fieldnames or "file" not in reader.fieldnames:
        raise CliException(
            "📝 The csv file is missing mandatory column 'file' to identify the picture's file in the external metadata csv file"
        )
    relevant_columns = [
        c for c in reader.fieldnames if (c in ["lat", "lon", "capture_time"] or c.startswith("Exif.") or c.startswith("Xmp."))
    ]

    if not relevant_columns:
        print(
            """⚠️ No relevant columns found in the external metadata csv file, the csv file will be ignored.
For more information on the external metadata file, check the documentation at https://docs.panoramax.fr/cli/USAGE/#external-metadata"""
        )
        return False
    else:
        print(f"📝 Metadata {', '.join((f'[bold]{c}[/bold]' for c in relevant_columns))} will be read from the external metadata csv file")
    return True


class CsvMetadataHandler(MetadataHandler):
    def __init__(self, data: Dict[str, reader.PartialGeoPicTags]) -> None:
        super().__init__()
        self.data = data

    @staticmethod
    def new_from_file(file_name: Path) -> Optional[CsvMetadataHandler]:
        if file_name.name != "panoramax.csv":
            return None

        data = CsvMetadataHandler._parse_file(file_name)
        if data is None:
            return None

        print(f"📝 Using csv file {file_name} as external metadata for the pictures")
        return CsvMetadataHandler(data)

    @staticmethod
    def _parse_file(file_name: Path) -> Optional[Dict[str, reader.PartialGeoPicTags]]:
        data = {}
        with open(file_name, "r") as f:
            # use Sniffer to detect the dialect of the file (separator, ...)
            try:
                dialect = csv.Sniffer().sniff(f.read(1024))
            except Exception as e:
                raise CliException(f"📝 The csv file {file_name} is not a valid csv file (error: {str(e)})")

            f.seek(0)
            reader = csv.DictReader(f, dialect=dialect)
            if not check(reader):
                return None

            for row in reader:
                val = CsvMetadataHandler.row_to_tag(row)
                if val:
                    pic_name, tag = val
                    data[pic_name] = tag

        return data

    @staticmethod
    def row_to_tag(row) -> Optional[Tuple[str, reader.PartialGeoPicTags]]:
        pic_name = row["file"]

        tags = reader.PartialGeoPicTags()

        tags.lat = utils.check_lat(row.get("lat"))
        tags.lon = utils.check_lon(row.get("lon"))
        tags.ts = utils.parse_capture_time(row.get("capture_time"))

        # Look for Exif/XMP columns
        tags.exif = {}
        for k in row:
            if k.startswith("Exif.") or k.startswith("Xmp."):
                v = row[k]
                if v is not None and len(v.strip()) > 0:
                    tags.exif[k] = row[k]

        return pic_name, tags

    def get(self, file_path: Path) -> Optional[reader.PartialGeoPicTags]:
        file_name = str(file_path.name)

        return self.data.get(str(file_name))
