def get_users_active_levels(hunt):
	""" Get a list of the levels this user is on or has completed. """
    return [x.level.number for x in hunt.active_levels]

def get_user_level_for_level(level, user):
	for user_level in level.user_levels:
		if user_level.hunt.user == user:
			return user_level

	# GRT Too generic an exception???
	raise Exception("Could not find user level for level")
