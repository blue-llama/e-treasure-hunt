from hunt.levels import get_latitude_longitude, valid_search, look_for_answers
import pytest
import mock


def test_get_latitude_longitude(rf):
    request = rf.get("/search", {"lat": 5.005, "long": -9.9})
    latitude, longitude = get_latitude_longitude(request)
    assert latitude == "5.005"
    assert longitude == "-9.9"


def test_invalid_search(rf):
    request = rf.get("/search", {"lat": 5.005})
    assert not valid_search(request)
    request = rf.get("/search", {"long": 5.005})
    assert not valid_search(request)
    request = rf.post("/search", {"lat": 5.005, "long": 5.005})
    assert not valid_search(request)


def test_valid_search(rf):
    request = rf.get("/do-search?lat=1.0&long=1.0")
    assert valid_search(request)


@mock.patch("hunt.levels.valid_search", return_value=False)
def test_look_for_answers_invalid_search(mock, rf):
    request = rf.get("/do-search?lat=1.0&long=1.0")
    assert look_for_answers(request) == "/search"