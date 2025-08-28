import os
from pathlib import Path
import httpx
import pytest

from panoramax_cli import download, model, upload
from tests.conftest import FIXTURE_DIR, MOCK_API_URL


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_retry(respx_mock, datafiles, tmp_path):
    """
    First 2 attempt at uploading a file will fail, but the 3rd one should be ok

    Same for attempt at downloading a file, and the other api calls
    """
    gvsMock = model.Panoramax(url=MOCK_API_URL)
    usId = "123456789"
    respx_mock.get(f"{MOCK_API_URL}/api").respond(json={})
    respx_mock.get(f"{MOCK_API_URL}/api/configuration").respond(json={})
    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets").respond(json={"id": usId})
    nb_calls_by_files = {"e1.jpg": 0, "e2.jpg": 0, "e3.jpg": 0}

    def file_upload_mocked(request):
        # the body will contains the name of the file in the multipart form, we can match on it
        c = request.content
        if b'filename="e1.jpg"' in c:
            f = "e1.jpg"
        elif b'filename="e2.jpg"' in c:
            f = "e2.jpg"
        elif b'filename="e3.jpg"' in c:
            f = "e3.jpg"
        else:
            raise Exception("should not receive other files")
        nb_calls_by_files[f] += 1
        if nb_calls_by_files[f] <= 2:
            return httpx.Response(502, json={"message": "ho no, something went wrong"})

        return httpx.Response(202, json={"picture_id": "bla"})

    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/files").mock(side_effect=file_upload_mocked)

    collection_id = "12345678-1234-5678-1234-567812345678"

    respx_mock.get(f"{MOCK_API_URL}/api/upload_sets/{usId}").mock(
        side_effect=[
            httpx.Response(502),
            httpx.Response(503),
            httpx.Response(
                200,
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
                    "associated_collections": [
                        {
                            "id": collection_id,
                            "nb_items": 3,
                            "ready": True,
                            "title": "some title",
                            "items_status": {
                                "broken": 0,
                                "not_processed": 0,
                                "prepared": 3,
                                "preparing": 0,
                            },
                            "links": [
                                {
                                    "rel": "self",
                                    "href": f"{MOCK_API_URL}/api/collections/{collection_id}",
                                    "type": "application/json",
                                }
                            ],
                        }
                    ],
                },
            ),
        ]
    )
    respx_mock.post(f"{MOCK_API_URL}/api/upload_sets/{usId}/complete").respond(json={})

    # Run upload
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=gvsMock,
        title="Test",
        uploadTimeout=20,
    )

    assert len(report.uploaded_files) == 3
    # No errors nor skipped files
    assert len(report.skipped_files) == 0
    assert len(report.errors) == 0

    # after the upload, we'll try to download the files, also with a flaky API
    files = sorted((tmp_path / "dl").rglob("*"))
    assert files == []

    print(f"{MOCK_API_URL}/api/collection/{collection_id}")
    respx_mock.get(f"{MOCK_API_URL}/api/collections/{collection_id}").mock(
        side_effect=[
            httpx.Response(502),
            httpx.Response(503),
            httpx.Response(
                200,
                json={
                    "id": collection_id,
                    "stats:items": {"count": 3},
                    "title": "shiny collection",
                },
            ),
        ]
    )
    respx_mock.get(f"{MOCK_API_URL}/api/collections/{collection_id}/items?limit=500").mock(
        side_effect=[
            httpx.Response(502),
            httpx.Response(503),
            httpx.Response(
                200,
                json={
                    "features": [
                        {
                            "id": "e1_id",
                            "assets": {
                                "hd": {
                                    "description": "Highest resolution available of this picture",
                                    "href": f"{MOCK_API_URL}/images/e1.jpg",
                                    "roles": ["data"],
                                    "title": "HD picture",
                                    "type": "image/jpeg",
                                },
                            },
                            "properties": {
                                "original_file:name": "e1.jpg",
                                "original_file:size": 12,
                            },
                        },
                        {
                            "id": "e2_id",
                            "assets": {
                                "hd": {
                                    "description": "Highest resolution available of this picture",
                                    "href": f"{MOCK_API_URL}/images/e2.jpg",
                                    "roles": ["data"],
                                    "title": "HD picture",
                                    "type": "image/jpeg",
                                },
                            },
                            "properties": {
                                "original_file:name": "e2.jpg",
                                "original_file:size": 12,
                            },
                        },
                        {
                            "id": "e3_id",
                            "assets": {
                                "hd": {
                                    "description": "Highest resolution available of this picture",
                                    "href": f"{MOCK_API_URL}/images/e3.jpg",
                                    "roles": ["data"],
                                    "title": "HD picture",
                                    "type": "image/jpeg",
                                },
                            },
                            "properties": {
                                "original_file:name": "e3.jpg",
                                "original_file:size": 12,
                            },
                        },
                    ],
                    "links": [],
                    "type": "FeatureCollection",
                },
            ),
        ]
    )
    with open(datafiles / "e1.jpg", "rb") as f:
        respx_mock.get(f"{MOCK_API_URL}/images/e1.jpg").mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(503),
                httpx.Response(200, content=f.read()),
            ]
        )

    with open(datafiles / "e2.jpg", "rb") as f:
        respx_mock.get(f"{MOCK_API_URL}/images/e2.jpg").mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(503),
                httpx.Response(200, content=f.read()),
            ]
        )

    with open(datafiles / "e3.jpg", "rb") as f:
        respx_mock.get(f"{MOCK_API_URL}/images/e3.jpg").mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(503),
                httpx.Response(200, content=f.read()),
            ]
        )

    download.download(
        collection=collection_id,
        panoramax=gvsMock,
        path=tmp_path / "dl",
        file_name="original-name",
    )
    files = sorted((tmp_path / "dl").rglob("*"))
    # we did not ask for external metadata, so no external metadata should be downloaded
    assert files == sorted(
        [
            tmp_path / "dl" / "shiny_collection",
            tmp_path / "dl" / "shiny_collection" / "e1.jpg",
            tmp_path / "dl" / "shiny_collection" / "e2.jpg",
            tmp_path / "dl" / "shiny_collection" / "e3.jpg",
        ]
    ), files
