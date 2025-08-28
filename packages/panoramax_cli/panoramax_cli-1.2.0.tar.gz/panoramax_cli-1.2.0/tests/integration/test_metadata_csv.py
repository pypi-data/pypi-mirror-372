import os
import pytest
from tests.conftest import FIXTURE_DIR
from pathlib import Path
import httpx
from panoramax_cli import status, upload, model
from datetime import timedelta
from geopic_tag_reader.sequence import SortMethod
from datetime import datetime
import shutil

from tests.integration.conftest import login, cleanup_panoramax


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "panoramax_exif.csv"),
)
def test_valid_csv_upload(panoramax_with_token, datafiles, user_credential, panoramax_with_token_for_elie):
    shutil.copy(datafiles / "panoramax_exif.csv", datafiles / "panoramax.csv")
    cleanup_panoramax(panoramax_with_token, panoramax_with_token_for_elie)
    # value stored in metadata.csv
    e1_new_lat = 50.5151
    e1_new_lon = 3.265
    e1_new_exif = {
        "Exif.Image.Software": "MS Paint",
        "Exif.Image.Artist": "A 2 years old",
        "Xmp.xmp.Rating": "1",
    }
    e3_new_lat = 50.513433333
    e3_new_lon = 3.265277778
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        uploadParameters=model.UploadParameters(sort_method=SortMethod.filename_asc),
    )
    assert len(report.upload_sets) == 1
    assert len(report.uploaded_files) == 3
    assert len(report.errors) == 0

    us = model.UploadSet(id=report.upload_sets[0].id)
    with httpx.Client() as c:
        login(c, panoramax_with_token, user_credential)
        status.wait_for_upload_sets(panoramax_with_token, c, [us], timeout=timedelta(minutes=1))
        us = status.get_uploadset_files(panoramax_with_token, c, us)
        us = status.info(panoramax_with_token, c, us)

    print(f"upload set == {us}")
    assert us.title == "some title"

    # 3 pictures should have been uploaded
    assert len(us.files) == 3

    for f in us.files:
        assert f.status == model.UploadFileStatus.synchronized

    # Check collections
    assert len(us.associated_collections) == 3
    c1 = httpx.get(f"{panoramax_with_token.url}/api/collections/{us.associated_collections[0].id}/items")
    c1.raise_for_status()
    c2 = httpx.get(f"{panoramax_with_token.url}/api/collections/{us.associated_collections[1].id}/items")
    c2.raise_for_status()
    c3 = httpx.get(f"{panoramax_with_token.url}/api/collections/{us.associated_collections[2].id}/items")
    c3.raise_for_status()

    c1 = c1.json()["features"]
    c2 = c2.json()["features"]
    c3 = c3.json()["features"]
    assert len(c1) == 1
    assert len(c2) == 1
    assert len(c3) == 1

    # Check pictures
    itemByFilename = {
        c1[0]["properties"]["original_file:name"]: c1[0],
        c2[0]["properties"]["original_file:name"]: c2[0],
        c3[0]["properties"]["original_file:name"]: c3[0],
    }
    assert len(itemByFilename) == 3

    assert itemByFilename["e1.jpg"]["geometry"]["coordinates"] == [
        e1_new_lon,
        e1_new_lat,
    ]
    assert datetime.fromisoformat(itemByFilename["e1.jpg"]["properties"]["datetime"]) == datetime.fromisoformat("2018-01-22T02:52:09+03:00")
    assert itemByFilename["e1.jpg"]["properties"]["exif"]["Exif.Image.Software"] == "MS Paint"
    assert itemByFilename["e1.jpg"]["properties"]["exif"]["Exif.Image.Artist"] == "A 2 years old"
    assert itemByFilename["e1.jpg"]["properties"]["exif"]["Xmp.xmp.Rating"] == "1"

    assert itemByFilename["e3.jpg"]["geometry"]["coordinates"] == [
        e3_new_lon,
        e3_new_lat,
    ]
    assert datetime.fromisoformat(itemByFilename["e3.jpg"]["properties"]["datetime"]) == datetime.fromisoformat("2018-01-22T02:54:09+03:00")
