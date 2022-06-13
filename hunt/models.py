from typing import Any, Type

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Team hunt progress info.
class HuntInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    level = models.IntegerField(default=1)
    hints_shown = models.IntegerField(default=1)
    hint_requested = models.BooleanField(default=False)
    next_hint_release = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user.get_username() + "_hunt"


@receiver(post_save, sender=User)
def create_hunt_info(
    sender: Type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    if created:
        HuntInfo.objects.create(user=instance)


# Level.
class Level(models.Model):
    number = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, default="", blank=True)
    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    tolerance = models.IntegerField()


# Hint
class Hint(models.Model):
    level = models.ForeignKey(Level, related_name="hints", on_delete=models.CASCADE)
    number = models.IntegerField()
    image = models.ImageField(upload_to="hints")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["level", "number"], name="unique hint")
        ]


# App settings. Use Boolean primary key to ensure there's only one active.
class AppSetting(models.Model):
    active = models.BooleanField(primary_key=True, default=True)
    use_alternative_map = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField()

    def __str__(self) -> str:
        TEXT = {
            HuntEvent.HINT_REQ: "requested a hint on",
            HuntEvent.HINT_REL: "saw a hint on",
            HuntEvent.CLUE_ADV: "progressed to",
        }
        user = self.user.get_username()
        text = f"At {self.time} {user} {TEXT[self.type]} level {self.level}"
        return text
