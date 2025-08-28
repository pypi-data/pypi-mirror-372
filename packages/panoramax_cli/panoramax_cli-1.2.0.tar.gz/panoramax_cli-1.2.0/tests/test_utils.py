from panoramax_cli import utils
import panoramax_cli
import pytest
import httpx


@pytest.mark.parametrize(
    ("local_version", "pypi_version", "up_to_date"),
    (
        ("0.1.0", "0.2.0", False),
        ("0.2.0", "0.2.1", False),
        ("0.2.0", "0.2.0", True),
        ("0.3.0", "0.2.0", True),
        ("1.0.0", "0.2.0", True),
    ),
)
def test_check_if_lastest_version(respx_mock, local_version, pypi_version, up_to_date):
    sub_pypi_response = {"info": {"version": pypi_version}}
    panoramax_cli.__version__ = local_version
    respx_mock.get("https://pypi.org/pypi/panoramax_cli/json").respond(json=sub_pypi_response)
    assert utils.check_if_lastest_version() == up_to_date


def test_check_if_lastest_version_skipped(respx_mock):
    respx_mock.get("https://pypi.org/pypi/panoramax_cli/json").mock(side_effect=httpx.ConnectTimeout)
    assert utils.check_if_lastest_version()
