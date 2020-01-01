from hunt.levels import get_latitude_longitude, valid_search
import pytest

def test_get_latitude_longitude(rf):
    request = rf.post('/search', {'lat': 5.005, 'long': -9.9 })
    latitude, longitude = get_latitude_longitude(request)
    assert latitude == '5.005'
    assert longitude == '-9.9'

def test_invalid_search(rf):
    request = rf.post('/search', {'lat': 5.005})
    assert not valid_search(request)
    request = rf.post('/search', {'long': 5.005})
    assert not valid_search(request)
    request = rf.get('/search', {'lat': 5.005, 'long': 5.005})
    assert not valid_search(request)

def test_valid_search(rf):
    request = rf.post('/search?lat=1.0&long=1.0')
    assert valid_search(request)