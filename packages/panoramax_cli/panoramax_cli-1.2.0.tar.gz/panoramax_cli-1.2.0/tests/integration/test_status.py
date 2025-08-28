import pytest
from panoramax_cli.status import get_uploadset_files
from panoramax_cli.exception import CliException
from panoramax_cli.model import UploadSet
import httpx


def test_status_on_unknown_uploadset(panoramax):
    with pytest.raises(CliException) as e:
        with httpx.Client() as c:
            get_uploadset_files(panoramax, c, UploadSet(id="blabla"))

    assert e.match("Upload Set blabla not found")
