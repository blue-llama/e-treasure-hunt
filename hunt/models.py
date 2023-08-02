from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


# Team hunt progress info.
class HuntInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    level = models.IntegerField(default=1)
    hints_shown = models.IntegerField(default=1)
    hint_requested = models.BooleanField(default=False)
    next_hint_release = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user.get_username()


@receiver(post_save, sender=User)
def create_hunt_info(
    sender: type[User],  # noqa: ARG001
    instance: User,
    created: bool,
    **kwargs: Any,  # noqa: ARG001
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

    def __str__(self) -> str:
        return f"Level {self.number}"


# Hint
class Hint(models.Model):
    level = models.ForeignKey(Level, related_name="hints", on_delete=models.CASCADE)
    number = models.IntegerField()
    image = models.ImageField(upload_to="hints")

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(fields=["level", "number"], name="unique hint")
        ]

    def __str__(self) -> str:
        return f"Level {self.level.number}, hint {self.number}"


@receiver(pre_delete, sender=Hint)
def hint_delete(
    sender: type[Hint],  # noqa: ARG001
    instance: Hint,
    **kwargs: Any,  # noqa: ARG001
) -> None:
    if instance.image:
        instance.image.delete(False)


# App settings. Use Boolean primary key to ensure there's only one active.
class AppSetting(models.Model):
    active = models.BooleanField(primary_key=True, default=True)
    use_alternative_map = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"App setting (active={self.active})"


# Event log for the hunt.
class HuntEvent(models.Model):
    HINT_REQ = "REQ"
    HINT_REL = "REL"
    CLUE_ADV = "ADV"
    EVENT_TYPES = (
        (HINT_REQ, "Hint requested"),
        (HINT_REL, "Hints released"),
        (CLUE_ADV, "Advanced level"),
    )

    time = models.DateTimeField()
    type = models.CharField(max_length=3, choices=EVENT_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.IntegerField()

    def __str__(self) -> str:
        actions = {
            HuntEvent.HINT_REQ: "requested a hint on",
            HuntEvent.HINT_REL: "saw a hint on",
            HuntEvent.CLUE_ADV: "progressed to",
        }
        user = self.user.get_username()
        text = f"At {self.time} {user} {actions[self.type]} level {self.level}"
        return text


class ChatMessage(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    room = models.CharField(max_length=255)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("date_added",)

    def __str__(self) -> str:
        return f"Room: {self.room}, User: {self.name}, Message: {self.content}"
