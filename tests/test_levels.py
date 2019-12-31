from hunt.levels import get_latitude_longitude, valid_search, is_correct_answer
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

@pytest.mark.django_db
def test_correct_answer(answer):
	assert is_correct_answer(1.23456789, -1.23456789, answer)

@pytest.mark.django_db
def test_incorrect_answer(answer):
	assert not is_correct_answer(1, -1, answer)
	assert not is_correct_answer(-1.23456789, 180 - (-1.23456789), answer)