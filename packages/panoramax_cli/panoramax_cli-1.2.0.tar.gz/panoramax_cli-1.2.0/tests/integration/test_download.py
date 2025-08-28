import os
import pytest
import httpx
import panoramax_cli.exception
import panoramax_cli.model
import panoramax_cli.status
import panoramax_cli.upload
import panoramax_cli.download
from tests.conftest import FIXTURE_DIR
from pathlib import Path
import shutil

from tests.integration.conftest import cleanup_panoramax


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_valid_collection_download(panoramax_with_token, datafiles, tmp_path):
    uploadReport = panoramax_cli.upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
        wait=True,
    )
    assert len(uploadReport.uploaded_files) == 3
    assert len(uploadReport.upload_sets) == 1
    assert len(uploadReport.upload_sets[0].associated_collections) == 1

    col_id = uploadReport.upload_sets[0].associated_collections[0].id

    with httpx.Client() as c:
        panoramax_cli.download.download_collection(
            client=c,
            collection_id=col_id,
            panoramax=panoramax_with_token,
            path=tmp_path / "dl",
            file_name="original-name",
        )
    path1 = tmp_path / "dl" / "some_title" / "e1.jpg"
    assert path1.exists()
    path2 = tmp_path / "dl" / "some_title" / "e2.jpg"
    assert path2.exists()
    path3 = tmp_path / "dl" / "some_title" / "e3.jpg"
    assert path3.exists()


@pytest.fixture(scope="module")
def load_data(panoramax_with_token, tmpdir_factory, panoramax_with_token_for_elie):
    import tempfile

    # do not use tmp_path since we want to use it as a fixture module
    tmp_dir = Path(tempfile.gettempdir())
    fixture_dir = Path(FIXTURE_DIR)

    tmp_dir = Path(tmpdir_factory.mktemp("panoramax_data"))

    dir1 = tmp_dir / "collection1"
    dir1.mkdir()
    dir2 = tmp_dir / "collection2"
    dir2.mkdir()
    shutil.copy(fixture_dir / "e1.jpg", dir1 / "e1.jpg")
    shutil.copy(fixture_dir / "e2.jpg", dir1 / "e2.jpg")
    shutil.copy(fixture_dir / "e3.jpg", dir2 / "e3.jpg")
    cleanup_panoramax(panoramax_with_token, panoramax_with_token_for_elie)

    uploadReport = panoramax_cli.upload.upload_path(
        path=tmp_dir,
        panoramax=panoramax_with_token,
        uploadTimeout=20,
        wait=True,
        title=None,
    )
    assert len(uploadReport.uploaded_files) == 3
    assert len(uploadReport.upload_sets) == 2
    assert len(uploadReport.upload_sets[0].associated_collections) == 1
    assert len(uploadReport.upload_sets[1].associated_collections) == 1
    return uploadReport


def test_valid_user_me_download(panoramax_with_token, tmp_path, load_data):
    # dir is empty at first
    files = sorted((tmp_path / "dl").rglob("*"))
    assert files == []

    panoramax_cli.download.download(
        user="me",
        panoramax=panoramax_with_token,
        path=tmp_path / "dl",
        file_name="original-name",
    )

    collections = []
    for path, dirs, files in os.walk(tmp_path / "dl"):
        if not path.endswith("/dl"):
            collections.append(Path(path))
    collections.sort()
    assert len(collections) == 2
    files = sorted((tmp_path / "dl").rglob("*"))

    # we did not ask for external metadata, so no external metadata should be downloaded
    assert files == sorted(
        [
            collections[0],
            collections[0] / "e1.jpg",
            collections[0] / "e2.jpg",
            collections[1],
            collections[1] / "e3.jpg",
        ]
    ), files
    e1_write_time = os.path.getmtime(collections[0] / "e1.jpg")
    e2_write_time = os.path.getmtime(collections[0] / "e2.jpg")
    e3_write_time = os.path.getmtime(collections[1] / "e3.jpg")
    # if we ask the same download, we should have some external metadata, and no data should have been downloaded
    panoramax_cli.download.download(
        user="me",
        panoramax=panoramax_with_token,
        path=tmp_path / "dl",
        file_name="original-name",
        external_metadata_dir_name="external_metadata",
    )
    files = sorted((tmp_path / "dl").rglob("*"))

    assert files == sorted(
        [
            collections[0],
            collections[0] / "e1.jpg",
            collections[0] / "external_metadata",
            collections[0] / "external_metadata" / "e1.jpg.json",
            collections[0] / "e2.jpg",
            collections[0] / "external_metadata" / "e2.jpg.json",
            collections[1],
            collections[1] / "e3.jpg",
            collections[1] / "external_metadata",
            collections[1] / "external_metadata" / "e3.jpg.json",
        ]
    ), files
    assert (collections[0] / "e1.jpg").exists()
    assert (collections[0] / "e2.jpg").exists()
    assert (collections[1] / "e3.jpg").exists()

    # since the picture was already downloaded, the download was skipped
    e1_write_time_after = os.path.getmtime(collections[0] / "e1.jpg")
    e2_write_time_after = os.path.getmtime(collections[0] / "e2.jpg")
    e3_write_time_after = os.path.getmtime(collections[1] / "e3.jpg")
    assert e1_write_time == e1_write_time_after
    assert e2_write_time == e2_write_time_after
    assert e3_write_time == e3_write_time_after


def test_invalid_user_id_download(panoramax_with_token, tmp_path, load_data):
    with pytest.raises(panoramax_cli.exception.CliException) as e:
        panoramax_cli.download.download(
            user="pouet",
            panoramax=panoramax_with_token,
            path=tmp_path / "dl",
            file_name="original-name",
        )
    assert str(e.value).startswith("Impossible to find user pouet")


def test_invalid_collection_id_download(panoramax_with_token, tmp_path, load_data):
    with pytest.raises(panoramax_cli.exception.CliException) as e:
        panoramax_cli.download.download(
            collection="pouet",
            panoramax=panoramax_with_token,
            path=tmp_path / "dl",
            file_name="original-name",
        )
    assert str(e.value).startswith("Impossible to get collection pouet"), e.value


def test_valid_user_id_download(panoramax_with_token, tmp_path, load_data):
    user = httpx.get(f"{panoramax_with_token.url}/api/users")
    user.raise_for_status()
    user_id = next(u["id"] for u in user.json()["users"] if u["name"] == "elysee")

    # we can download even without a token
    panoramax_cli.download.download(
        user=user_id,
        panoramax=panoramax_cli.model.Panoramax(url=panoramax_with_token.url),
        path=tmp_path / "dl",
        file_name="id",
    )
    # if we ask by id, we got the id as file_name
    col1_upload_set = next(u for u in load_data.upload_sets if len(u.files) == 2)
    col2_upload_set = next(u for u in load_data.upload_sets if len(u.files) == 1)
    pic1_id = col1_upload_set.files[0].picture_id
    pic2_id = col1_upload_set.files[1].picture_id
    pic3_id = col2_upload_set.files[0].picture_id
    print(f"pic1_id={pic1_id}, pic2_id={pic2_id}, pic3_id={pic3_id}")

    # Find folder names matching collection 1 & 2
    collections = []
    for path, dirs, files in os.walk(tmp_path / "dl"):
        if not path.endswith("/dl"):
            collections.append(Path(path))
    collections.sort()
    assert len(collections) == 2
    print(f"col1={list((collections[0]).iterdir())}")
    print(f"col2={list((collections[1]).iterdir())}")
    assert (collections[0] / f"{pic1_id}.jpg").exists()
    assert (collections[0] / f"{pic2_id}.jpg").exists()
    assert (collections[1] / f"{pic3_id}.jpg").exists()

    # we can also download with a lower quality
    panoramax_cli.download.download(
        user=user_id,
        panoramax=panoramax_cli.model.Panoramax(url=panoramax_with_token.url),
        path=tmp_path / "dl_sd",
        file_name="id",
        quality=panoramax_cli.download.Quality.sd,
    )
    assert (tmp_path / "dl_sd" / collections[0].stem / f"{pic1_id}.jpg").exists()
    assert (tmp_path / "dl_sd" / collections[0].stem / f"{pic2_id}.jpg").exists()
    assert (tmp_path / "dl_sd" / collections[1].stem / f"{pic3_id}.jpg").exists()

    panoramax_cli.download.download(
        user=user_id,
        panoramax=panoramax_cli.model.Panoramax(url=panoramax_with_token.url),
        path=tmp_path / "dl_thumb",
        file_name="id",
        quality=panoramax_cli.download.Quality.thumb,
    )

    assert (tmp_path / "dl_thumb" / collections[0].stem / f"{pic1_id}.jpg").exists()
    assert (tmp_path / "dl_thumb" / collections[0].stem / f"{pic2_id}.jpg").exists()
    assert (tmp_path / "dl_thumb" / collections[1].stem / f"{pic3_id}.jpg").exists()

    size = lambda p: os.path.getsize(p)

    for c, f in [
        (collections[0].stem, f"{pic1_id}.jpg"),
        (collections[0].stem, f"{pic2_id}.jpg"),
        (collections[1].stem, f"{pic3_id}.jpg"),
    ]:
        assert size(tmp_path / "dl_thumb" / c / f) <= size(tmp_path / "dl_sd" / c / f)
        assert size(tmp_path / "dl_sd" / c / f) <= size(tmp_path / "dl" / c / f)
