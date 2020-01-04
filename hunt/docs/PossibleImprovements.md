# Possible Improvements

## Support different number of clues/hints

Currently all levels must have 5 clues. The infrastructure for displaying hints shouldn't be too difficult to change.
- Add the number of hints to the Level model
- level.can_request_hint should be updated
- level.get_hints_to_show should get the correct number of hints

The infrastructure for uploading a varying number of hints is slightly harder. LevelForm needs updating to support multiple images, 
this is somewhat tricky for Django, because the ImageField now needs to be a ForeignKey to another Model where each model is an ImageField.