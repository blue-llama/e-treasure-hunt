from django.core.exceptions import ValidationError
from hunt.models import Level, Location, Answer
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


def validate_answer_name(value):
    try:
        # If an answer with this name already exists we can't create another
        Answer.objects.get(name=value)
        raise ValidationError(f"Answer name already exists.")
    except Answer.DoesNotExist:
        return