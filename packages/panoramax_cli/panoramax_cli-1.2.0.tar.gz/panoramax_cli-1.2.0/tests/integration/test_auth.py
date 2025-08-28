from panoramax_cli import upload
from panoramax_cli import auth, exception, model
import os
import pytest
from pathlib import Path
from tests.conftest import FIXTURE_DIR
from tests.integration.conftest import login
import httpx


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_auth_with_token(panoramax_with_token, datafiles):
    report = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax_with_token,
        title="some title",
        uploadTimeout=20,
    )

    assert len(report.uploaded_files) == 3
    assert len(report.errors) == 0


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_login(panoramax, datafiles, user_credential, tmp_path):
    assert not os.path.exists(tmp_path / "geovisio" / "config.toml")
    l = auth.create_auth_credentials(panoramax)

    # we call the auth credentials while loggin
    with httpx.Client() as c:
        login(c, panoramax, user_credential)
        claim = c.get(l.get_claim_url())
        assert claim.status_code == 200
        assert claim.text == "You are now logged in the CLI, you can upload your pictures"

    assert os.path.exists(tmp_path / "geovisio" / "config.toml")

    # doing a panoramax upload should work without crendentials now
    uploadReport = upload.upload_path(
        path=Path(datafiles),
        panoramax=panoramax,
        title="some title",
        uploadTimeout=20,
    )
    assert len(uploadReport.uploaded_files) == 3
    assert len(uploadReport.errors) == 0


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_login_without_claim(panoramax, datafiles, tmp_path):
    """Login without claiming the token should result to errors for pictures upload"""
    assert not os.path.exists(tmp_path / "geovisio" / "config.toml")
    l = auth.create_auth_credentials(panoramax)

    # a config file should have been created
    assert os.path.exists(tmp_path / "geovisio" / "config.toml")

    # doing a panoramax upload should not work as the token is not usable yet
    with pytest.raises(
        exception.CliException,
        match="🔁 Computer not authenticated yet, impossible to upload pictures, but you can try again the same upload command after finalizing the login",
    ):
        upload.upload_path(
            path=Path(datafiles),
            panoramax=panoramax,
            title="some title",
            uploadTimeout=20,
        )


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_login_on_invalid_url_path(panoramax_with_token, datafiles):
    with pytest.raises(exception.CliException) as e:
        auth.create_auth_credentials(model.Panoramax(url=panoramax_with_token.url + "/some_additional_path"))
    msg = str(e.value)
    assert msg.startswith(
        f"""The API URL is not valid.

Note that your URL should be the API root (something like https://panoramax.openstreetmap.fr, https://panoramax.ign.fr or any other panoramax instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {panoramax_with_token.url}/some_additional_path/api
[bold]Error:[/bold]"""
    )
