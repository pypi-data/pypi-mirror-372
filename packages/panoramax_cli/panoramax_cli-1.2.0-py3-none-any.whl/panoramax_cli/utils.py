from panoramax_cli.exception import CliException
from rich import print
import httpx

REQUESTS_CNX_TIMEOUT = (
    15.1  # max number of seconds to wait for the connection to establish, cf https://www.python-httpx.org/advanced/timeouts/
)
REQUESTS_TIMEOUT = httpx.Timeout(connect=REQUESTS_CNX_TIMEOUT, read=30, pool=5, write=30)
REQUESTS_TIMEOUT_STATUS = httpx.Timeout(connect=REQUESTS_CNX_TIMEOUT, read=120, pool=5, write=30)


def test_panoramax_url(client: httpx.Client, panoramax: str):
    full_url = f"{panoramax}/api"
    try:
        r = client.get(full_url, timeout=REQUESTS_TIMEOUT)
    except (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.TimeoutException,
        httpx.TooManyRedirects,
    ) as e:
        raise CliException(
            f"""The API is not reachable. Please check error and used URL below, and retry later if the URL is correct.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )
    except Exception as e:
        raise CliException(
            f"""Error while connecting to the API. Please check error and used URL below

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )

    if r.status_code == 404:
        raise CliException(
            f"""The API URL is not valid.

Note that your URL should be the API root (something like https://panoramax.openstreetmap.fr, https://panoramax.ign.fr or any other panoramax instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{r.text}"""
        )
    if r.status_code > 404:
        raise CliException(
            f"""The API is unavailable for now. Please check given error and retry later.
[bold]Used URL:[/bold] {full_url}
[bold]Error[/bold] (code [cyan]{r.status_code}[/cyan]):
{r.text}"""
        )


def check_if_lastest_version():
    from packaging import version
    import panoramax_cli

    pypi_url = "https://pypi.org/pypi/panoramax_cli"

    try:
        response = httpx.get(f"{pypi_url}/json", timeout=REQUESTS_TIMEOUT)
        latest_version = response.json()["info"]["version"]

        if version.parse(latest_version) > version.parse(panoramax_cli.__version__):
            print(
                f"""⚠️ A newer panoramax_cli version {latest_version} is available on PyPI (available on {pypi_url}).
We highly recommend updating as this tool is still in active development, and new versions ensure good compatibility with Panoramax API.
To update it, check the documentation at https://docs.panoramax.fr/cli/INSTALL/#updating-an-existing-installation"""
            )
            return False

    except httpx.TimeoutException:
        print("Skip check to verify if CLI version is latest (PyPI timeout)")
    except httpx.HTTPError as e:
        print(f"Skip check to verify if CLI version is latest ({e})")

    return True


def removeNoneInDict(val):
    """Removes empty values from dictionnary"""
    return {k: v for k, v in val.items() if v is not None}
