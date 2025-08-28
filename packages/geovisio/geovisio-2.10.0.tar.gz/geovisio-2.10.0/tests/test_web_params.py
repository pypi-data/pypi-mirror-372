from geovisio.web import params
import datetime
from dateutil import tz


def test_parse_utc_datetime():
    p = params.parse_datetime("2020-05-31T10:00:00Z", error="")
    assert p.tzname() == "UTC"

    # if it was dateutil or datetime that parsed the date, the timezone can either datetime.timezone.utc ot tzutc()
    p_tz = p.tzinfo
    assert p_tz in (datetime.timezone.utc, tz.tzutc())
    p = p.astimezone(tz.UTC)
    assert p == datetime.datetime(2020, 5, 31, 10, 0, tzinfo=datetime.timezone.utc)


def test_parse_utc_datetime_interval():
    min, max = params.parse_datetime_interval("2020-05-31T10:00:00Z")
    assert min and max

    assert min.tzname() == "UTC"
    assert max.tzname() == "UTC"

    # if it was dateutil or datetime that parsed the date, the timezone can either datetime.timezone.utc ot tzutc()
    min_tz = min.tzinfo
    assert min_tz in (datetime.timezone.utc, tz.tzutc())
    min = min.astimezone(tz.UTC)
    assert min == datetime.datetime(2020, 5, 31, 10, 0, tzinfo=datetime.timezone.utc)
    max_tz = max.tzinfo
    assert max_tz in (datetime.timezone.utc, tz.tzutc())
    max = max.astimezone(tz.UTC)
    assert max == datetime.datetime(2020, 5, 31, 10, 0, tzinfo=datetime.timezone.utc)
