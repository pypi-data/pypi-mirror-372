import os
import pytest

from tests.conftest import FIXTURE_DIR
from pathlib import Path
import httpx
from panoramax_cli import model, exception, upload
from datetime import timedelta
from geopic_tag_reader.sequence import SortMethod, SplitParams, MergeParams
import shutil
from panoramax_cli.status import wait_for_upload_sets, info, get_uploadset_files
from tests.integration.conftest import login


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_valid_upload(panoramax_with_token, datafiles, user_credential):
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
    )
    assert len(report.upload_sets) == 1
    assert len(report.uploaded_files) == 3
    assert len(report.errors) == 0

    with httpx.Client() as c:
        login(c, panoramax_with_token, user_credential)
        wait_for_upload_sets(panoramax_with_token, c, report.upload_sets, timeout=timedelta(minutes=1))
        us = model.UploadSet(id=report.upload_sets[0].id)
        us = info(panoramax_with_token, c, us)
        us = get_uploadset_files(panoramax_with_token, c, us)

    assert len(us.files) == 3
    assert len(us.associated_collections) == 1

    for f in us.files:
        assert f.status == model.UploadFileStatus.synchronized

    # the collection should also have 3 items
    collection = httpx.get(f"{panoramax_with_token.url}/api/collections/{us.associated_collections[0].id}/items")
    collection.raise_for_status()

    features = collection.json()["features"]
    assert len(features) == 3


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_resume_upload(panoramax_with_token, datafiles):
    # Make e2 not valid to have a partial upload
    picE2 = datafiles / "e2.jpg"
    picE2bak = datafiles / "e2.bak"
    os.rename(picE2, picE2bak)
    with open(picE2, "w") as picE2file:
        picE2file.write("")
        picE2file.close()

    # Start upload -> 2 uploaded pics + 1 failure
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        uploadParameters=model.UploadParameters(sort_method=SortMethod.filename_asc),
    )
    assert len(report.upload_sets) == 1
    assert len(report.uploaded_files) == 2
    assert len(report.errors) == 0
    assert len(report.skipped_files) == 1
    assert report.skipped_files[0].path == datafiles / "e2.jpg"

    # Make e2 valid
    os.remove(picE2)
    os.rename(picE2bak, picE2)

    # Launch again upload : 1 uploaded pic + 0 failure
    report2 = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        uploadParameters=model.UploadParameters(sort_method=SortMethod.filename_asc),
    )
    assert report2.upload_sets[0].id == report.upload_sets[0].id
    assert len(report2.uploaded_files) == 1
    assert report2.uploaded_files[0].path == datafiles / "e2.jpg"
    assert report2.errors == []
    assert set([f.path.name for f in report2.skipped_files]) == {
        "e1.jpg",
        "e3.jpg",
    }  # Should not try to upload previous files


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_upload_twice(panoramax_with_token, datafiles):
    """Uploading twice the same sequence, should result on nothing done in the second upload"""

    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
    )
    assert len(report.upload_sets) == 1
    assert len(report.uploaded_files) == 3
    assert len(report.errors) == 0

    report2 = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
    )
    assert len(report2.upload_sets) == 1
    assert report2.upload_sets[0].id == report.upload_sets[0].id
    assert len(report2.uploaded_files) == 0
    assert len(report2.errors) == 0
    assert len(report2.skipped_files) == 3
    for f in report2.skipped_files:
        assert f.status == model.UploadFileStatus.synchronized


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_upload_with_duplicates(panoramax_with_token, datafiles):
    # Create a duplicate of e1
    shutil.copyfile(datafiles / "e1.jpg", datafiles / "e0.jpg")

    # Start upload
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
    )
    assert len(report.upload_sets) == 1
    assert report.errors == []
    assert len(report.skipped_files) == 1
    assert len(report.uploaded_files) == 3, report.uploaded_files


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_upload_with_upload_parameters(panoramax_with_token, datafiles):
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        uploadParameters=upload.UploadParameters(
            relative_heading=90,
            split_params=SplitParams(maxDistance=10, maxTime=120),
            merge_params=MergeParams(maxDistance=3, maxRotationAngle=55),
            sort_method=SortMethod.filename_desc,
        ),
    )
    assert len(report.upload_sets) == 1
    assert report.errors == []

    r = httpx.get(f"{panoramax_with_token.url}/api/upload_sets/{report.upload_sets[0].id}")
    assert r.status_code == 200
    r = r.json()
    assert r["relative_heading"] == 90
    assert r["split_distance"] == 10
    assert r["split_time"] == 120
    # No deduplication done by the API since it has already been done
    assert r.get("duplicate_rotation") is None
    assert r.get("duplicate_distance") is None
    assert r["sort_method"] == "filename-desc"
    assert r["no_deduplication"] is True
    assert r["metadata"] == {"cli_configuration": {"duplicate_distance": 3, "duplicate_rotation": 55}}


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_upload_without_deduplication_nor_split(panoramax_with_token, datafiles):
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        uploadParameters=upload.UploadParameters(
            relative_heading=90,
            split_params=None,
            merge_params=None,
            sort_method=SortMethod.filename_desc,
        ),
    )
    assert len(report.upload_sets) == 1
    assert report.errors == []

    r = httpx.get(f"{panoramax_with_token.url}/api/upload_sets/{report.upload_sets[0].id}")
    assert r.status_code == 200
    r = r.json()
    assert r["relative_heading"] == 90
    assert r.get("split_distance") is None
    assert r.get("split_time") is None
    assert r.get("duplicate_rotation") is None
    assert r.get("duplicate_distance") is None
    assert r["no_deduplication"] is True
    assert r["no_split"] is True
    assert r["sort_method"] == "filename-desc"
    assert r["metadata"] == {"cli_configuration": {"no_deduplication": True}}


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_host(datafiles):
    with pytest.raises(exception.CliException) as e:
        upload.upload_path(
            path=Path(datafiles),
            panoramax=model.Panoramax(url="http://some_invalid_url"),
            title="some title",
            uploadTimeout=20,
        )
    msg = str(e.value)
    assert msg.startswith(
        """The API is not reachable. Please check error and used URL below, and retry later if the URL is correct.

[bold]Used URL:[/bold] http://some_invalid_url/api
[bold]Error:[/bold]"""
    )

    # First one for local testing, second one for CI...
    assert (
        "Temporary failure in name resolution" in msg or "No address associated with hostname" in msg or "Name or service not known" in msg
    )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_path(panoramax_with_token, datafiles):
    with pytest.raises(exception.CliException) as e:
        upload.upload_path(
            path=Path(datafiles),
            panoramax=model.Panoramax(url=panoramax_with_token.url + "/some_additional_path"),
            title=None,
            uploadTimeout=20,
        )
    msg = str(e.value)
    assert msg.startswith(
        f"""The API URL is not valid.

Note that your URL should be the API root (something like https://panoramax.openstreetmap.fr, https://panoramax.ign.fr or any other panoramax instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {panoramax_with_token.url}/some_additional_path/api
[bold]Error:[/bold]"""
    )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_on_invalid_url_schema(datafiles):
    with pytest.raises(exception.CliException) as e:
        upload.upload_path(
            path=Path(datafiles),
            panoramax=model.Panoramax(url="a non valid url at all"),
            title=None,
            uploadTimeout=20,
        )
    assert str(e.value).startswith(
        """Error while connecting to the API. Please check error and used URL below

[bold]Used URL:[/bold] a non valid url at all/api
[bold]Error:[/bold]"""
    )
