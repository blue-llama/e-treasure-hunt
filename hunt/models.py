from django.contrib.auth.models import User
from django.db import models


# Team hunt progress info.
class HuntInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    hints_shown = models.IntegerField(default=1)
    hint_requested = models.BooleanField(default=False)
    next_hint_release = models.DateTimeField(null=True, blank=True)
    slack_channel = models.CharField(max_length=16, default="", blank=True)

    def __str__(self) -> str:
        return self.user.username + "_hunt"


# Level.
class Level(models.Model):
    number = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    latitude = models.DecimalField(max_digits=13, decimal_places=7)
    longitude = models.DecimalField(max_digits=13, decimal_places=7)
    tolerance = models.IntegerField()
    clues = models.CharField(max_length=500)


# Hint release time (start of 40 minute window, UTC).
class HintTime(models.Model):
    time = models.TimeField()

    def __str__(self) -> str:
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

    def __str__(self) -> str:
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
