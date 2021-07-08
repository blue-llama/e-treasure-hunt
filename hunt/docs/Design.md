# High Level Design

## Database Models

The infrastructure of the hunt is stored using 5 different Models, which can broadly be separated into 2 distinct categories:
1. The layout of the hunt
	1. Level
	1. Answer
	1. Location
1. Objects tracking the progress through a hunt
	1. HuntInfo
	1. UserLevel

Additionally, much of the infrastructure relies on Django's built-in `User` model documented [here](https://docs.djangoproject.com/en/3.0/ref/contrib/auth/#django.contrib.auth.models.User)

### Layout

The layout of the hunt can be thought of as a Directed Graph with Levels representing vertices and Answers representing edges. Locations are tightly coupled to Answers (there is a one-to-one mapping) and exist purely to simplify validation of forms.

A hunt is made up of any number of levels, connected by answers.

#### Level

A Level is a puzzle that must be solved by working out one or more answers given by a single clue image. An additional 4 hint images may be requested by the user to help solve the level. 

A Level displays the previous level's Location, Name and Description. 

#### Answer

An Answer links 2 Levels together. An Answer solves a given Level and leads to a given Level. A Level may be solved by multiple Answers and multiple Answers may Lead
to a single level.

The physical search co-ordinates of an Answer is given by a Location.

#### Location

A Location is a geographical point (longitude and latitude) with a tolerance (in metres). This represents the position the user must search (within the given tolerance) in order to correctly provide an answer to a Level.

### Progress

#### HuntInfo

A HuntInfo object is required for each user participating in the hunt. The HuntInfo object stores a list of all UserLevels for it's user.

#### UserLevel

A UserLevel object tracks the progress of a user through the layout of a hunt. For each user, there may exist one UserLevel referencing each Level object in the hunt. If a UserLevel exists for a Level, the user has access to that Level (and may attempt to provide Answers solved by that Level). If a UserLevel for the Level does not exist, the user may not access that Level (or attempt to solve it).

## Operations

Here's how the various operations requested by the user are carried out

### Accessing a Level of the Hunt

* The HTTP request includes both the user and the level number attempting to be accessed
* We get a list of level numbers available to the user by looking up all the Levels for the UserLevel objects that exist for this user's HuntInfo. Staff are given access to all level numbers. If a UserLevel linking to the Level of this number exists, the user has access.
* We get the Name, Location and Description to display on the Level by looking for an Answer which leads_to the level being requested. While there may be several Answers which lead to this level, we assume the first has the required information.
* We look up the UserLevel object for this user and level number. For staff, we may have to create this object. This tells us how many hints to display on the Level.
* We display the number of images determined from the Level's clues.

### Requesting a hint for a Level

* The HTTP request includes both the user and the level number that the user is requesting a hint for.
* We look up the UserLevel corresponding to this Level for this User. We mark on the UserLevel that a hint has been requested.

User's may request hints for any level they have access to (even if they have already moved past the level).

### Releasing hints

* We spin through all UserLevel objects, if a hint has been requested for that UserLevel, we increment the number of hints to show and reset the hint requested flag.

### Guessing answers to Levels

* The HTTP request includes both the user and the level number that the user is trying to guess the answer to.
* We look up the Level object for this level number. For each answer to this level:
	* Get the Location for this Answer
	* Check if the given co-ordinations are close enough to the Location's position (less than the tolerance away from the co-ordinates)
	* If the answer is correct, advance.
		* Create a new UserLevel object for the user to the Level indicated by the Answers leads_to parameter.

## Example

A worked example of objects that exist as a hunt is in progress can be found [here](ExampleObjects.md)
