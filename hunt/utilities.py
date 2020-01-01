from hunt.models import Level


def get_users_active_levels(hunt):
    """ Get a list of the levels this user is on or has completed. """
    return sorted([x.level.number for x in hunt.active_levels.all()], reverse=True)


def get_user_level_for_level(level, user):
    for user_level in level.user_levels.all():
        if user_level.hunt.user == user:
            return user_level

    raise RuntimeError("Could not find user level for level")


def get_all_level_numbers():
    return list(Level.objects.order_by("-number").values_list("number", flat=True))


def get_max_level_number():
    return Level.objects.order_by("-number")[0].number
