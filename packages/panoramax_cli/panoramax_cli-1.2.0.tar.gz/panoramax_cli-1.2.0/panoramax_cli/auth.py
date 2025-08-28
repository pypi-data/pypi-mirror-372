from panoramax_cli.http import createClientWithRetry, Client
from panoramax_cli.model import Panoramax
from panoramax_cli.exception import raise_for_status
from panoramax_cli.utils import test_panoramax_url
import os
from dataclasses import dataclass, field
from typing import List, Optional
import tomli
import tomli_w
from rich import print


def login(c: Client, panoramax: Panoramax) -> bool:
    """
    Login to panoramax and store auth cookie in client
    """
    if panoramax.token is not None:
        return _login_with_token(c, panoramax)

    return _login_with_stored_credentials(c, panoramax)


def _login_with_token(c: Client, panoramax: Panoramax) -> bool:
    c.headers.update({"Authorization": f"Bearer {panoramax.token}"})
    return True


def _login_with_stored_credentials(c: Client, panoramax: Panoramax):
    creds = _read_existing_credentials(panoramax)

    instance_cred = creds.get_instance_credentials(panoramax.url)
    if not instance_cred:
        _generate_and_update_credentials(c, creds, panoramax)
        return False

    account_name = _check_if_associated(c, panoramax, instance_cred)
    if not account_name:
        claim_url = f"{panoramax.url}/api/auth/tokens/{instance_cred.token_id}/claim"
        print(
            "🔐 We're waiting for you to link your user account with generated API token. To finalize authentication, please either go to the URL below, or scan the QR code below."
        )
        print(claim_url)
        _display_qr_code(claim_url)
        return False

    print(f"👤 Using stored credentials, logged in as [bold]{account_name}[/bold]")
    c.headers.update({"Authorization": f"Bearer {instance_cred.jwt_token}"})
    return True


@dataclass
class InstanceCredential:
    url: str
    jwt_token: str
    token_id: str

    def get_claim_url(self) -> str:
        return f"{self.url}/api/auth/tokens/{self.token_id}/claim"


@dataclass
class Credentials:
    instances: List[InstanceCredential] = field(default_factory=lambda: [])

    def from_toml(self, data):
        self.instances = [
            InstanceCredential(url=i["url"], jwt_token=i["jwt_token"], token_id=i["token_id"]) for i in data.get("instances", [])
        ]

    def toml(self):
        return {"instances": [{"url": i.url, "jwt_token": i.jwt_token, "token_id": i.token_id} for i in self.instances]}

    def get_instance_credentials(self, instance_url: str):
        return next((c for c in self.instances if c.url == instance_url), None)


def create_auth_credentials(panoramax: Panoramax, disable_cert_check: bool = False) -> InstanceCredential:
    """
    Login to panoramax and store auth cookie in client
    """
    with createClientWithRetry(disable_cert_check) as c:
        test_panoramax_url(c, panoramax.url)
        creds = _read_existing_credentials(panoramax)

        instance_cred = creds.get_instance_credentials(panoramax.url)
        if instance_cred:
            account_name = _check_if_associated(c, panoramax, instance_cred)
            if account_name:
                print(f"👤 Already logged to instance as [bold]{account_name}[/bold]")
                return instance_cred
            claim_url = instance_cred.get_claim_url()
            print(
                "🔐 We're waiting for you to link your user account with generated API token. To finalize authentication, please either go to the URL below, or scan the QR code below."
            )
            print(claim_url)
            _display_qr_code(claim_url)
            return instance_cred

        return _generate_and_update_credentials(c, creds, panoramax)


def _generate_and_update_credentials(client: Client, creds: Credentials, panoramax: Panoramax) -> InstanceCredential:
    i = _generate_new_instance_credentials(client, panoramax)

    creds.instances.append(i)

    _write_credentials(creds)
    return i


def get_config_file_path() -> str:
    # store config file either if [XDG](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) defined directory or in a user specifig .config directory
    config_file_dir = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")

    return os.path.join(config_file_dir, "geovisio", "config.toml")


def _read_existing_credentials(panoramax: Panoramax) -> Credentials:
    creds = Credentials()
    if not os.path.exists(get_config_file_path()):
        return creds

    with open(get_config_file_path(), "rb") as f:
        creds.from_toml(tomli.load(f))
        f.close()
    return creds


def _generate_new_instance_credentials(client: Client, panoramax: Panoramax) -> InstanceCredential:
    token_response = client.post(f"{panoramax.url}/api/auth/tokens/generate")
    raise_for_status(token_response, "Impossible to generate a Panoramax token")

    token = token_response.json()
    jwt_token = token["jwt_token"]
    id = token["id"]

    claim_url = next(li["href"] for li in token["links"] if li["rel"] == "claim")
    print(
        f"🔐 Your computer is not yet authorized against Panoramax API {panoramax.url}. To authenticate, please either go to the URL below, or scan the QR code below."
    )
    print(claim_url)
    _display_qr_code(claim_url)
    return InstanceCredential(url=panoramax.url, jwt_token=jwt_token, token_id=id)


def _write_credentials(creds: Credentials):
    config_file_path = get_config_file_path()
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    with open(config_file_path, "wb") as f:
        tomli_w.dump(creds.toml(), f)
        f.close()


def _check_if_associated(client: Client, panoramax: Panoramax, creds: InstanceCredential) -> Optional[str]:
    token_response = client.get(
        f"{panoramax.url}/api/users/me",
        headers={"Authorization": f"Bearer {creds.jwt_token}"},
    )
    if token_response.status_code == 403 or token_response.status_code == 401:
        return None
    raise_for_status(token_response, "Impossible to get token status")

    return token_response.json()["name"]


def _display_qr_code(url):
    import qrcode
    import io

    qr = qrcode.QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())
