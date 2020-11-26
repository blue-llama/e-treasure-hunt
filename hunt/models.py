from typing import Any, Dict, Type

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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


@receiver(post_save, sender=User)
def create_hunt_info(
    sender: Type[User], instance: User, created: bool, **kwargs: Dict[str, Any]
) -> None:
    if created:
        HuntInfo.objects.create(user=instance)


# Level.
class Level(models.Model):
    number = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    latitude = models.DecimalField(max_digits=13, decimal_places=7)
    longitude = models.DecimalField(max_digits=13, decimal_places=7)
    tolerance = models.IntegerField()


# Hint
class Hint(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    number = models.IntegerField()
    image = models.FileField(upload_to="hints")


# App settings. Use Boolean primary key to ensure there's only one active.
# Could make this into a table with string key-values, but we'd lose automatic
# field types, and need to parse them from strings.
class AppSetting(models.Model):
    active = models.BooleanField(primary_key=True)
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
        string_rep = "At " + str(self.time) + " " + self.team.upper() + " "

        if self.type == HuntEvent.HINT_REQ:
            string_rep += "requested a hint on level " + str(self.level)
        elif self.type == HuntEvent.CLUE_ADV:
            string_rep += "progressed to level " + str(self.level)
        else:
            string_rep += "saw a hint on level " + str(self.level)

        return string_rep
