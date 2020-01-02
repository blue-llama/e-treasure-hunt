from django.core.exceptions import ValidationError
from hunt.models import Level, Location
import json


def validate_answer_file(value):
    answer_json = json.loads(value.read())

    for field in ["latitude", "longitude", "tolerance"]:
        if not answer_json.get(field):
            raise ValidationError(f"Missing {field} from answer.")

    location = Location(
        latitude=answer_json.get('latitude'),
        longitude=answer_json.get('longitude'),
        tolerance=answer_json.get('tolerance')
    )
    try:
        location.full_clean()
    except:
        raise ValidationError(f"Answer location is not valid.")


def validate_all_hints_provided(value):
    if len(value != 4):
        raise ValidationError(f"Must provide 4 hints.")
