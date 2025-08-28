import pytest
import os

from panoramax_cli import upload, exception, model
from tests.conftest import FIXTURE_DIR, MOCK_API_URL
from pathlib import Path
import httpx
from geopic_tag_reader.reader import PartialGeoPicTags
import datetime
import json
import shutil


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_path_to_upload_sets_basic(datafiles):
    p = model.UploadParameters()
    sets = upload.path_to_upload_sets(Path(datafiles), p)
    assert len(sets) == 1
    us = sets[0]
    assert us.path == datafiles
    assert us.parameters == p
    assert len(us.files) == 3
    f = set([str(f.path) for f in us.files])
    assert f == {
        str(datafiles / "e1.jpg"),
        str(datafiles / "e2.jpg"),
        str(datafiles / "e3.jpg"),
    }
    for f in us.files:
        assert f.externalMetadata is None


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_path_to_upload_sets_subfolders(datafiles):
    # Prepare subfolders
    us1Path = os.path.join(datafiles, "us1")
    us2Path = os.path.join(datafiles, "us2")
    us3Path = os.path.join(datafiles, "us3")
    os.mkdir(us1Path)
    os.mkdir(us2Path)
    os.mkdir(us3Path)
    os.rename(os.path.join(datafiles, "e1.jpg"), os.path.join(us1Path, "e1.jpg"))
    os.rename(os.path.join(datafiles, "e2.jpg"), os.path.join(us2Path, "e2.jpg"))
    os.rename(os.path.join(datafiles, "e3.jpg"), os.path.join(us3Path, "e3.jpg"))

    # Test function
    p = model.UploadParameters()
    sets = upload.path_to_upload_sets(Path(datafiles), p)
    assert set((str(us.path) for us in sets)) == {us1Path, us2Path, us3Path}

    for us in sets:
        assert len(us.files) == 1
        assert us.parameters == p
        assert us.files[0].externalMetadata is None

    files_by_us_name = {us.path.name: [f.path.name for f in us.files] for us in sets}
    assert files_by_us_name == {"us1": ["e1.jpg"], "us2": ["e2.jpg"], "us3": ["e3.jpg"]}


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_path_to_upload_sets_subfolders_merge(datafiles):
    # Prepare subfolders
    us1Path = os.path.join(datafiles, "us1")
    us2Path = os.path.join(datafiles, "us2")
    us3Path = os.path.join(datafiles, "us3")
    os.mkdir(us1Path)
    os.mkdir(us2Path)
    os.mkdir(us3Path)
    p1 = os.path.join(us1Path, "e1.jpg")
    p2 = os.path.join(us2Path, "e2.jpg")
    p3 = os.path.join(us3Path, "e3.jpg")
    os.rename(os.path.join(datafiles, "e1.jpg"), p1)
    os.rename(os.path.join(datafiles, "e2.jpg"), p2)
    os.rename(os.path.join(datafiles, "e3.jpg"), p3)

    # Test function
    p = model.UploadParameters()
    sets = upload.path_to_upload_sets(Path(datafiles), p, True)
    assert len(sets) == 1
    uset = sets[0]
    assert uset.path == Path(datafiles)
    assert set([str(f.path) for f in uset.files]) == {p1, p2, p3}


@pytest.mark.parametrize(
    ("picture", "result"),
    (
        (model.UploadFile(path=Path("."), externalMetadata=None), {}),
        (
            model.UploadFile(path=Path("."), externalMetadata=PartialGeoPicTags()),
            {},
        ),
        (
            model.UploadFile(
                path=Path("."), externalMetadata=PartialGeoPicTags(lon=42, model="MAKE")
            ),  # api does not handle overriding model for the moment so it's not in the end result
            {"override_longitude": 42},
        ),
        (
            model.UploadFile(
                path=Path("."),
                externalMetadata=PartialGeoPicTags(
                    lat=12,
                    type="flat",
                    ts=datetime.datetime(1970, 1, 5, 21, 50, 42, tzinfo=datetime.timezone.utc),
                ),
            ),  # api does not handle overriding type for the moment so it's not in the end result
            {
                "override_latitude": 12,
                "override_capture_time": "1970-01-05T21:50:42+00:00",
            },
        ),
        (
            model.UploadFile(
                path=Path("."),
                externalMetadata=PartialGeoPicTags(exif={"Exif.Image.Software": "Hugin", "Xmp.xmp.Rating": "5"}),
            ),
            {"override_Exif.Image.Software": "Hugin", "override_Xmp.xmp.Rating": "5"},
        ),
    ),
)
def test_get_overriden_metadata(picture, result):
    assert upload._get_overriden_metadata(picture) == result


def mock_api_post_collection_fail(respx_mock):
    respx_mock.post(MOCK_API_URL + "/api/upload_sets").mock(side_effect=httpx.ConnectTimeout)


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_set_creation_failure(respx_mock, datafiles):
    mock_api_post_collection_fail(respx_mock)

    with pytest.raises(exception.CliException) as e:
        upload.upload_path(
            path=datafiles,
            panoramax=model.Panoramax(url=MOCK_API_URL),
            title="Test",
            uploadTimeout=20,
        )

    assert str(e.value).startswith("Error while connecting to the API")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_set_creation_failure_incompatible(respx_mock, datafiles):
    respx_mock.get(MOCK_API_URL + "/api").respond(status_code=200)
    respx_mock.get(MOCK_API_URL + "/api/configuration").respond(json={}, status_code=200)
    respx_mock.post(MOCK_API_URL + "/api/upload_sets").respond(status_code=404)

    with pytest.raises(exception.CliException) as e:
        upload.upload_path(
            path=Path(datafiles),
            panoramax=model.Panoramax(url=MOCK_API_URL),
            title="Test",
            uploadTimeout=20,
        )

    assert str(e.value).startswith("Panoramax API doesn't support Upload Set")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_upload_with_invalid_file(respx_mock, datafiles):
    # Mock upload set creation
    gvsMock = model.Panoramax(url=MOCK_API_URL)
    usId = "123456789"
    respx_mock.get(f"{MOCK_API_URL}/api").respond(json={})
    respx_mock.get(f"{MOCK_API_URL}/api/configuration").respond(json={})
    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets").respond(json={"id": usId})

    # the body will contains the name of the file in the multipart form, we can match on it

    def file_upload_mocked(request):
        c = request.content
        if b'filename="e1.jpg"' in c:
            return httpx.Response(202, json={"picture_id": "bla"})
        if b'filename="e2.jpg"' in c:
            return httpx.Response(400)
        if b'filename="e3.jpg"' in c:
            return httpx.Response(409)
        raise Exception("should not receive other files")

    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/files").mock(side_effect=file_upload_mocked)
    respx_mock.get(f"{MOCK_API_URL}/api/upload_sets/{usId}").respond(
        json={
            "completed": False,
            "dispatched": False,
            "ready": False,
            "sort_method": "filename_asc",
            "split_distance": 100,
            "split_time": 300,
            "duplicate_distance": 2,
            "duplicate_rotation": 30,
            "items_status": {
                "prepared": 0,
                "preparing": 1,
                "broken": 2,
                "not_processed": 0,
            },
            "associated_collections": None,
        },
    )
    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/complete").respond(json={})

    # Run upload
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=gvsMock,
        title="Test",
        uploadTimeout=20,
    )

    assert len(report.uploaded_files) == 1
    assert len(report.skipped_files) == 1
    assert len(report.errors) == 1

    assert str(report.uploaded_files[0].path) == os.path.join(datafiles, "e1.jpg")
    assert str(report.errors[0].file.path) == os.path.join(datafiles, "e2.jpg")
    assert report.errors[0].status_code == 400
    assert str(report.skipped_files[0].path) == os.path.join(datafiles, "e3.jpg")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_upload_folder_dots(respx_mock, datafiles):
    # Prepare subfolders
    us1Path = os.path.join(datafiles, "us1.anyname.lol")
    os.mkdir(us1Path)
    p1 = os.path.join(us1Path, "e1.jpg")
    os.rename(os.path.join(datafiles, "e1.jpg"), p1)

    # Mock upload set creation
    gvsMock = model.Panoramax(url=MOCK_API_URL)
    usId = "123456789"
    respx_mock.get(f"{MOCK_API_URL}/api").respond(json={})
    respx_mock.get(f"{MOCK_API_URL}/api/configuration").respond(json={})

    def us_post(request):
        c = request.content
        if b'title="us1.anyname.lol"':
            return httpx.Response(200, json={"id": usId})
        raise Exception("title not matching")

    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets").mock(side_effect=us_post)

    # the body will contains the name of the file in the multipart form, we can match on it
    def file_upload_mocked(request):
        c = request.content
        if b'filename="e1.jpg"' in c:
            return httpx.Response(202, json={"picture_id": "bla"})
        raise Exception("should not receive other files")

    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/files").mock(side_effect=file_upload_mocked)

    respx_mock.get(f"{MOCK_API_URL}/api/upload_sets/{usId}").respond(
        json={
            "completed": False,
            "dispatched": False,
            "ready": False,
            "sort_method": "filename_asc",
            "split_distance": 100,
            "split_time": 300,
            "duplicate_distance": 2,
            "duplicate_rotation": 30,
            "items_status": {
                "prepared": 0,
                "preparing": 1,
                "broken": 0,
                "not_processed": 0,
            },
            "associated_collections": None,
        },
    )
    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/complete").respond(json={})

    # Run upload
    report = upload.upload_path(
        path=Path(us1Path),
        panoramax=gvsMock,
        uploadTimeout=20,
        title=None,
    )

    assert len(report.uploaded_files) == 1
    assert len(report.skipped_files) == 0
    assert len(report.errors) == 0
    assert str(report.uploaded_files[0].path) == os.path.join(us1Path, "e1.jpg")


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"),
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_local_checks_reportfile(datafiles):
    picf = Path(datafiles)

    # Create a duplicate
    shutil.copy(picf / "e3.jpg", picf / "e4.jpg")

    reportFile = picf / "report.json"
    upload.local_checks(
        picf,
        model.UploadParameters(
            sort_method=model.SortMethod.filename_asc,
            merge_params=model.MergeParams(maxDistance=2),
        ),
        False,
        reportFile,
    )

    assert reportFile.exists()

    with reportFile.open("r", encoding="utf-8") as f:
        res = json.load(f)

        assert len(res["pictures_exif_issues"]) == 1
        assert res["pictures_exif_issues"][0] == {
            "path": str(picf / "e1_without_exif.jpg"),
            "issue": "The picture is missing mandatory metadata:\n\t- No GPS coordinates or broken coordinates in picture EXIF tags\n\t- No valid date in picture EXIF tags",
        }

        assert len(res["pictures_duplicates"]) == 1
        assert res["pictures_duplicates"][0] == "e4.jpg"

        assert len(res["folders"]) == 1
        assert res["folders"][0]["path"] == str(picf.resolve())
        assert len(res["folders"][0]["sequences"]) == 1
        assert len(res["folders"][0]["sequences_splits"]) == 0
        seq = res["folders"][0]["sequences"][0]
        assert seq["pictures_nb"] == 3
        assert seq["pictures_files"] == ["e1.jpg", "e2.jpg", "e3.jpg"]
