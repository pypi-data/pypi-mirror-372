import pytest
import os
from panoramax_cli.model import Panoramax
import httpx


@pytest.fixture(scope="session")
def panoramax(pytestconfig):
    """
    If --external-panoramax-url has been given to pytest use an already running panoramax, else spawn a fully configured panoramax for integration tests
    """
    external_panoramax_url = pytestconfig.getoption("--external-panoramax-url")
    if external_panoramax_url:
        yield Panoramax(url=external_panoramax_url)
        return

    from testcontainers import compose

    dco_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "docker-compose-panoramax.yml",
    )
    with compose.DockerCompose(
        ".",
        compose_file_name=dco_file,
        pull=True,
    ) as compose:
        port = compose.get_service_port("panoramax-api", 5000)
        api_url = f"http://api.panoramax.localtest.me:{port}"
        compose.wait_for(api_url)

        yield Panoramax(url=api_url)
        stdout, stderr = compose.get_logs()
        if stderr:
            print("Errors\n:{}".format(stderr))


@pytest.fixture(scope="session")
def user_credential():
    """Credential of a fake created account on keycloak"""
    return ("elysee", "my password")


@pytest.fixture(scope="session")
def user_elie_credential():
    """Credential of a fake created account on keycloak"""
    return ("elie_reclus", "my password")


@pytest.fixture(scope="session")
def panoramax_with_token(panoramax, user_credential):
    token = _get_token(panoramax, user_credential)
    return Panoramax(
        url=panoramax.url,
        token=token,
    )


@pytest.fixture(scope="session")
def panoramax_with_token_for_elie(panoramax, user_elie_credential):
    token = _get_token(panoramax, user_elie_credential)
    return Panoramax(
        url=panoramax.url,
        token=token,
    )


@pytest.fixture(scope="session")
def user_elysee_id(panoramax, user_credential):
    return _get_user_id(panoramax, user_credential)


@pytest.fixture(scope="session")
def user_elie_id(panoramax, user_elie_credential):
    return _get_user_id(panoramax, user_elie_credential)


def _get_user_id(panoramax, cred):
    token = _get_token(panoramax, cred)
    r = httpx.get(f"{panoramax.url}/api/users/me", headers={"Authorization": f"Bearer {token}"}).raise_for_status()
    return r.json()["id"]


def _get_token(panoramax, user_credential):
    with httpx.Client() as c:
        login(c, panoramax, user_credential)
        tokens = c.get(f"{panoramax.url}/api/users/me/tokens", follow_redirects=True).raise_for_status()
        token_link = next(t["href"] for t in tokens.json()[0]["links"] if t["rel"] == "self")
        assert token_link
        jwt_token = c.get(token_link, follow_redirects=True)
        jwt_token.raise_for_status()
        return jwt_token.json()["jwt_token"]


def login(client, panoramax, user_credential):
    login = client.get(f"{panoramax.url}/api/auth/login", follow_redirects=True)

    url = _get_keycloak_authenticate_form_url(login)

    r = client.post(
        url,
        data={"username": user_credential[0], "password": user_credential[1]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=True,
    )

    # a bit hacky, but since for the moment we only submit a form to keycloak, to know if the login was successful,
    # we need to check that we were redirected to panoramax
    r.raise_for_status()
    assert r.history != 0


def _get_keycloak_authenticate_form_url(response):
    """Little hack to parse keycloak HTML to get the url to the authenticate form"""
    import re

    url = re.search('action="(.*login-actions/authenticate[^"]*)"', response.text)

    assert url, f"impossible to find form action in keycloak response: {response.text}"
    url = url.group(1).replace("&amp;", "&")
    return url


@pytest.fixture(scope="function", autouse=True)
def override_config_home(tmp_path):
    """Set XDG_CONFIG_HOME to temporary directory, so tests newer write a real user config file"""
    old_var = os.environ.get("XDG_CONFIG_HOME")

    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    yield

    if old_var:
        os.environ["XDG_CONFIG_HOME"] = old_var
    else:
        del os.environ["XDG_CONFIG_HOME"]


def cleanup_panoramax(panoramax_with_token, panoramax_with_token_for_elie):
    """Delete all collections on panoramax"""
    cleanup_user_collections(panoramax_with_token)
    cleanup_user_collections(panoramax_with_token_for_elie)


def cleanup_user_collections(panoramax):
    """Delete all user's collections on panoramax"""
    existing_cols = httpx.get(
        f"{panoramax.url}/api/users/me/collection",
        follow_redirects=True,
        headers={"Authorization": f"Bearer {panoramax.token}"},
    )
    if existing_cols.status_code == 404:
        return
    for c in existing_cols.raise_for_status().json()["links"]:
        if c["rel"] != "child":
            continue
        httpx.delete(
            f"{panoramax.url}/api/collections/{c['id']}",
            headers={"Authorization": f"Bearer {panoramax.token}"},
        ).raise_for_status()
