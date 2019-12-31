def get_users_active_levels(hunt):
    """ Get a list of the levels this user is on or has completed. """
    return [x.level.number for x in hunt.active_levels.all()]

def get_user_level_for_level(level, user):
    for user_level in level.user_levels.all():
        if user_level.hunt.user == user:
            return user_level

    raise RuntimeError("Could not find user level for level")
