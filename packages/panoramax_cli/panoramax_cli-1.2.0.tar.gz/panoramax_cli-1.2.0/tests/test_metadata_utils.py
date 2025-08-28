import pytest
from panoramax_cli.metadata import utils
import datetime
from panoramax_cli import exception


def test_parse_capture_time():
    r = utils.parse_capture_time("2018-01-22T02:52:09.999346+00:00")
    assert r == datetime.datetime(
        year=2018,
        month=1,
        day=22,
        hour=2,
        minute=52,
        second=9,
        microsecond=999346,
        tzinfo=datetime.timezone.utc,
    )


def test_parse_bad_date_capture_time():
    with pytest.raises(exception.CliException) as e:
        utils.parse_capture_time("plop")
    assert str(e.value) == "The capture_time was not recognized (should follow the RFC 3339): plop (Invalid isoformat string: 'plop')"
