from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Team hunt progress info.
class HuntInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="huntinfo"
    )
    # Effectively has the following fields:
    # active_levels - a list of this user's active levels
    def __str__(self):
        return self.user.username + "_hunt"


class Location(models.Model):
    """
    A location for which there can be an answer. This exists so that we can validate creation of these objects
    """

    latitude = models.DecimalField(
        max_digits=13,
        decimal_places=7,
        validators=[MaxValueValidator(90), MinValueValidator(-90)],
        default=0,
    )
    longitude = models.DecimalField(
        max_digits=13,
        decimal_places=7,
        validators=[MaxValueValidator(180), MinValueValidator(-180)],
        default=0,
    )
    tolerance = models.IntegerField(
        validators=[MaxValueValidator(10000)], default=100
    )  # Don't allow a tolerance any greater than 10km


class Level(models.Model):
    number = models.IntegerField(primary_key=True)
    clues = models.CharField(max_length=500)
    # Effectively has the following fields:
    # answers - A list of answers to this level
    # user_levels - The user specific portion of this level, one for each hunt/user


class Answer(models.Model):
    """
    Answer to a level, this needs to be a separate model such that a level can have multiple answers (hence the ForeignKey)
    """

    location = models.OneToOneField(
        Location, on_delete=models.CASCADE, related_name="answer"
    )
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField(max_length=5000)
    # Which level does this answer solve
    solves_level = models.ForeignKey(
        Level, on_delete=models.CASCADE, null=True, related_name="answers"
    )
    # Which level should this answer lead to
    leads_to_level = models.ForeignKey(
        Level, on_delete=models.CASCADE, blank=True, null=True, related_name="+"
    )


class UserLevel(models.Model):
    """
    A class representing a single level for a user. UserLevels track the progress of a user through the hunt, so UserLevels only exist
    for levels a team has completed or is working on.
    """
    # Each hunt has multiple levels, so use a ForeignKey
    hunt = models.ForeignKey(
        HuntInfo, on_delete=models.CASCADE, null=True, related_name="active_levels"
    )
    # Each level can be solved by each user, so use a ForeignKey
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE, null=True, related_name="user_levels"
    )
    hints_shown = models.IntegerField(default=1)
    hint_requested = models.BooleanField(default=False)


# Hint release time (start of 40 minute window, UTC).
class HintTime(models.Model):
    time = models.TimeField()

    def __str__(self):
        string_rep = "Hint for " + str(self.time) + " UTC - expect 0-40 mins later"
        return string_rep


# App settings. Use Boolean primary key to ensure there's only one active.
# Could make this into a table with string key-values, but we'd lose automatic
# field types, and need to parse them from strings.
class AppSetting(models.Model):
    active = models.BooleanField(primary_key=True)
    next_hint = models.DateTimeField(default=0)
    last_max_level = models.IntegerField(default=1)
    max_level = models.IntegerField(default=1)
    use_alternative_map = models.BooleanField(default=False)


# Event log for the hunt.
class HuntEvent(models.Model):
    HINT_REQ = "REQ"
    HINT_REL = "REL"
    CLUE_ADV = "ADV"
    EVENT_TYPES = [
        (HINT_REQ, "Hint requested"),
        (HINT_REL, "Hints released"),
        (CLUE_ADV, "Advanced level"),
    ]

    time = models.DateTimeField()
    type = models.CharField(max_length=3, choices=EVENT_TYPES)
    team = models.CharField(max_length=127, default="")
    level = models.IntegerField(default=0)

    def __str__(self):
        string_rep = "At " + str(self.time) + " "

        if self.type == HuntEvent.HINT_REQ:
            string_rep += (
                self.team.upper() + " requested a hint on level " + str(self.level)
            )
        elif self.type == HuntEvent.CLUE_ADV:
            string_rep += self.team.upper() + " progressed to level " + str(self.level)
        else:
            string_rep += "a hint was added on level " + str(self.level)

        return string_rep
