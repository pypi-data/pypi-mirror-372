import pytest
import os
from panoramax_cli.metadata import csv
from panoramax_cli import exception
from tests.conftest import FIXTURE_DIR
from geopic_tag_reader.reader import PartialGeoPicTags
from pathlib import Path
import datetime


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "panoramax.csv"),
)
def test_CsvMetadataHandler(datafiles):
    mtd = csv.CsvMetadataHandler.new_from_file(Path(datafiles / "panoramax.csv"))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(
            lat=50.5151,
            lon=3.265,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:52:09+00:00"),
        ),
        "e3.jpg": PartialGeoPicTags(
            lat=50.513433333,
            lon=3.265277778,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:54:09+00:00"),
        ),
    }


def test_CsvMetadataHandler_invalid_name(datafiles):
    mtd = csv.CsvMetadataHandler.new_from_file(Path(datafiles / "pouet.csv"))
    assert mtd is None


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "panoramax_exif.csv"),
)
def test_CsvMetadataHandler_exif(datafiles):
    import shutil

    shutil.copy(datafiles / "panoramax_exif.csv", datafiles / "panoramax.csv")
    mtd = csv.CsvMetadataHandler.new_from_file(Path(datafiles / "panoramax.csv"))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(
            lat=50.5151,
            lon=3.265,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:52:09+03:00"),
            exif={
                "Exif.Image.Software": "MS Paint",
                "Exif.Image.Artist": "A 2 years old",
                "Xmp.xmp.Rating": "1",
            },
        ),
        "e3.jpg": PartialGeoPicTags(
            lat=50.513433333,
            lon=3.265277778,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:54:09+03:00"),
        ),
    }


def test_bad_lat_CsvMetadataHandler(datafiles):
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,lon,lat,capture_time,field_of_view,heading
e1.jpg,3.265,lat,2018-01-22T02:52:09+00:00,,
"""
        )
    with pytest.raises(exception.CliException) as e:
        csv.CsvMetadataHandler.new_from_file(Path(p))
    assert str(e.value) == "Impossible to parse latitude (could not convert string to float: 'lat')"


def _assert_in_logs(msg, capsys):
    captured = capsys.readouterr()
    # Note: we must strip \n from the output since rich's print add them for more readability
    # and since some \n are replaced with spacing, we also strip spacing
    assert msg.replace("\n", "").replace(" ", "") in captured.out.replace("\n", "").replace(" ", ""), captured.out


def test_empty_file(datafiles, capsys):
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(r"")

    with pytest.raises(exception.CliException) as e:
        csv.CsvMetadataHandler.new_from_file(Path(p))
    assert str(e.value) == f"📝 The csv file {p} is not a valid csv file (error: Could not determine delimiter)"


def test_missing_column(datafiles, capsys):
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(
            r"""plop,pouet
12,14
"""
        )

    with pytest.raises(exception.CliException) as e:
        csv.CsvMetadataHandler.new_from_file(Path(p))
    assert (
        str(e.value)
        == "📝 The csv file is missing mandatory column 'file' to identify the picture's file in the external metadata csv file"
    )


def test_only_file_column(datafiles, capsys):
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,
12,
"""
        )
    r = csv.CsvMetadataHandler.new_from_file(Path(p))
    assert r is None
    _assert_in_logs(
        """⚠️ No relevant columns found in the external metadata csv file, the csv file will be ignored.
For more information on the external metadata file, check the documentation at https://docs.panoramax.fr/cli/USAGE/#external-metadata""",
        capsys,
    )


def test_not_all_column(datafiles, capsys):
    """The csv can lack some column, we should only have a log on this"""
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,lon,lat
e1.jpg,3.265,12
"""
        )
    r = csv.CsvMetadataHandler.new_from_file(Path(p))
    assert r is not None  # we can read it
    _assert_in_logs(
        f"📝 Metadata lon, lat will be read from the external metadata csv file📝 Using csv file {p} as external metadata for the pictures",
        capsys,
    )


def test_bad_date_CsvMetadataHandler(datafiles):
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        f.write(
            r"""file,lon,lat,capture_time,field_of_view,heading
e1.jpg,3.265,12,plop,,
"""
        )
    with pytest.raises(exception.CliException) as e:
        csv.CsvMetadataHandler.new_from_file(Path(p))
    assert str(e.value) == "The capture_time was not recognized (should follow the RFC 3339): plop (Invalid isoformat string: 'plop')"


@pytest.mark.parametrize(("delimiter"), ((","), (";"), ("\t")))
def test_tsv_delimiter(datafiles, delimiter):
    """Using other delimiter should also be a valid"""
    p = datafiles / "panoramax.csv"
    with open(p, "w") as f:
        r = r"""file;lon;lat;capture_time;field_of_view;heading
e1.jpg;3.265;50.5151;2018-01-22T02:52:09+00:00;;
e3.jpg;3.265277778;50.513433333;2018-01-22T02:54:09+00:00;360;15
""".replace(";", delimiter)
        f.write(r)
    mtd = csv.CsvMetadataHandler.new_from_file(Path(p))
    assert mtd.data == {
        "e1.jpg": PartialGeoPicTags(
            lat=50.5151,
            lon=3.265,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:52:09+00:00"),
        ),
        "e3.jpg": PartialGeoPicTags(
            lat=50.513433333,
            lon=3.265277778,
            ts=datetime.datetime.fromisoformat("2018-01-22T02:54:09+00:00"),
        ),
    }
