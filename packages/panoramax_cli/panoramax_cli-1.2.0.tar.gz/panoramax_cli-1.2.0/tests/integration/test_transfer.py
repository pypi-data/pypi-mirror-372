import pytest
import httpx
import panoramax_cli.exception
import panoramax_cli.model
import panoramax_cli.status
import panoramax_cli.upload
import panoramax_cli.transfer
from tests.conftest import FIXTURE_DIR
from pathlib import Path
import shutil

from tests.integration.conftest import cleanup_user_collections, login


@pytest.fixture
def load_data(panoramax_with_token, panoramax_with_token_for_elie, tmpdir_factory):
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
    cleanup_user_collections(panoramax_with_token)
    cleanup_user_collections(panoramax_with_token_for_elie)

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


def test_valid_collection_transfer(
    panoramax_with_token,
    user_elie_credential,
    panoramax_with_token_for_elie,
    user_credential,
    load_data,
):
    """Transfer a collection in the same panoramax instance, but between user.
    Collection is originaly owned by elysee, and is copied to elie_reclus"""
    with httpx.Client() as from_client, httpx.Client() as to_client:
        login(from_client, panoramax_with_token, user_credential)
        login(to_client, panoramax_with_token, user_elie_credential)

        # elie should not have any collections at first

        assert (
            to_client.get(
                f"{panoramax_with_token_for_elie.url}/api/users/me/collection",
                follow_redirects=True,
            ).status_code
            == 404
        )

        usid = panoramax_cli.transfer.transfer_collection(
            from_collection=load_data.upload_sets[0].associated_collections[0].id,
            from_api=panoramax_with_token,
            to_api=panoramax_with_token,
            from_client=from_client,
            to_client=to_client,
            picture_request_timeout=20,
            parallel_transfers=1,
        )
        panoramax_cli.status.wait_for_upload_sets(panoramax_with_token, to_client, [panoramax_cli.model.UploadSet(id=usid)])
        us = panoramax_cli.status.get_uploadset_files(panoramax_with_token, to_client, panoramax_cli.model.UploadSet(id=usid))
        assert len(us.files) > 0

        # the destination upload set should have the metadata
        u = httpx.get(f"{panoramax_with_token_for_elie.url}/api/upload_sets/{usid}").raise_for_status()

        assert u.json()["metadata"] == {
            "original:collection_id": load_data.upload_sets[0].associated_collections[0].id,
            "original:instance": panoramax_with_token.url,
        }

        # We can access the upload set with elysee credentials, but not picture_id should be included
        us_elysee = panoramax_cli.status.get_uploadset_files(
            panoramax_with_token,
            from_client,
            panoramax_cli.model.UploadSet(id=usid),
        )
        for f in us_elysee.files:
            assert f.picture_id is None

        # and the collections should be owned by elie
        existing_cols = to_client.get(
            f"{panoramax_with_token_for_elie.url}/api/users/me/collection",
            follow_redirects=True,
        ).raise_for_status()
        cols_id = {c["id"] for c in existing_cols.json()["links"] if c["rel"] == "child"}
        assert len(cols_id) > 0


def test_valid_user_me_transfer(panoramax_with_token, load_data, user_credential):
    usIds = panoramax_cli.transfer.transfer(
        from_api=panoramax_with_token,
        to_api=panoramax_with_token,
        from_user="me",
    )

    with httpx.Client() as c:
        panoramax_cli.status.wait_for_upload_sets(
            panoramax_with_token,
            c,
            [panoramax_cli.model.UploadSet(id=u) for u in usIds],
        )
        login(c, panoramax_with_token, user_credential)
        us = [panoramax_cli.status.get_uploadset_files(panoramax_with_token, c, panoramax_cli.model.UploadSet(id=usid)) for usid in usIds]
        assert len(us) == 2
        assert sum([len(u.files) for u in us]) == 3


def test_invalid_user_id_transfer(panoramax_with_token, load_data):
    with pytest.raises(panoramax_cli.exception.CliException) as e:
        panoramax_cli.transfer.transfer(
            from_api=panoramax_with_token,
            to_api=panoramax_with_token,
            from_user="prout",
        )
    assert str(e.value).startswith("Impossible to find user prout")


def test_invalid_collection_id_transfer(panoramax_with_token, load_data):
    with pytest.raises(panoramax_cli.exception.CliException) as e:
        panoramax_cli.transfer.transfer(
            from_api=panoramax_with_token,
            to_api=panoramax_with_token,
            from_collection="prout",
        )
    assert str(e.value).startswith("Impossible to get collection prout"), e.value


def test_valid_user_id_transfer(panoramax_with_token, load_data, user_credential):
    user = httpx.get(f"{panoramax_with_token.url}/api/users")
    user.raise_for_status()
    user_id = next(u["id"] for u in user.json()["users"] if u["name"] == "elysee")

    usIds = panoramax_cli.transfer.transfer(
        from_api=panoramax_with_token,
        to_api=panoramax_with_token,
        from_user=user_id,
    )

    with httpx.Client() as c:
        panoramax_cli.status.wait_for_upload_sets(
            panoramax_with_token,
            c,
            [panoramax_cli.model.UploadSet(id=u) for u in usIds],
        )
        login(c, panoramax_with_token, user_credential)
        us = [panoramax_cli.status.get_uploadset_files(panoramax_with_token, c, panoramax_cli.model.UploadSet(id=usid)) for usid in usIds]
        assert len(us) == 2
        assert sum([len(u.files) for u in us]) == 3
