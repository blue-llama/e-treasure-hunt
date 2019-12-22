from django.db import models
from django.contrib.auth.models import User

# Team hunt progress info.
class HuntInfo(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE,  null=True)
  hint_requested = models.BooleanField(default=False)
  private_hint_requested = models.BooleanField(default=False)
  private_hints_shown = models.IntegerField(default=0)
  private_hint_allowed = models.BooleanField(default=False)
  def __str__(self):
    return self.user.username + "_hunt"

# Level.
class Level(models.Model):
    number = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000)
    clues = models.CharField(max_length=500)

# Answer to a level, this needs to be a separate model such that a level can have multiple answers (hence the ForeignKey)
class Answer(models.Model):
    latitude = models.DecimalField(max_digits=13, decimal_places=7)
    longitude = models.DecimalField(max_digits=13, decimal_places=7)
    tolerance = models.IntegerField()
    # Which level does this answer apply to
    level = models.ForeignKey(Level, on_delete=models.CASCASE)

# Each level can be solved independelty by a team
class UserLevel(models.Model)
    user = models.OneToOneField(User, on_delete=models.CASCADE,  null=True)
    hints_shown = models.IntegerField(default=1)
    hint_requested = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    
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
    HINT_REQ = 'REQ'
    HINT_REL = 'REL'
    CLUE_ADV = 'ADV'
    EVENT_TYPES = [
        (HINT_REQ, 'Hint requested'),
        (HINT_REL, 'Hints released'),
        (CLUE_ADV, 'Advanced level'),
    ]
    
    time = models.DateTimeField()
    type = models.CharField(max_length=3, choices=EVENT_TYPES)
    team = models.CharField(max_length=127, default="")
    level = models.IntegerField(default=0)
    
    def __str__(self):
        string_rep = "At " + str(self.time) + " "
        
        if (self.type == HuntEvent.HINT_REQ):
            string_rep += self.team.upper() + " requested a hint on level " + str(self.level)
        elif (self.type == HuntEvent.CLUE_ADV):
            string_rep += self.team.upper() + " progressed to level " + str(self.level)
        else:
            string_rep += "a hint was added on level " + str(self.level)
            
        return string_rep