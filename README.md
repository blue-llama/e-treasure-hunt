# Setup

You will need:
- Heroku account
- Dropbox account, with an app set up with read/write permission to a folder to hold the images, and an OAuth key
- Google Cloud account with maps APIs enabled, and API key
- Heroku CLI installed

## Initial Configuration

Setup:
- Create your Heroku app
- Set the DJ_KEY environment variable to a secret string
- Set the DB_TOKEN environment variable to your DropBox OAuth token
- Set the GM_API_KEY environment variable to your Google API key
- Set the APP_URL environment variable to the root domain for your app (e.g. example.com)
- Add a Heroku Postgres add-on to your app

Deploy:
- Deploy the app to Heroku
- Use the CLI to run 'heroku run -a <app_name> python manage.py createsuperuser' and set up an admin user

Admin initiation:
- Navigate to <domain>/admin
- Create a HuntInfo object for the admin user
- Create an AppSetting object - tick "active" and set next hint release to now
- Create HintTime objects for all required hint release windows

# Hunt Infrastructure
Infrastructure for the Hunt is stored as 3 different object types:
1. Levels
1. Answers
1. Locations

## Level

A hunt is made up of a number of levels. Each level has a 5 clue images, the first of which is always visible and the remainder are released
after being requested by the user.

Levels are linked together by answers.

## Answer

An Answer links 2 Levels together. An Answer solves a given Level and leads to a given Level. A Level may be solved by multiple Answers and multiple Answers may Lead
to a single level.

The physical search co-ordinates of an Answer is given by a Location.

## Location

A Location is a geographical point (longitude and latitude) with a tolerance (in metres). There is a one-to-one mapping of Answer to Location.

## Viewing the Hunt

You can view the current hunt layout by navigating to \<domain\>/level-graph.

# Creating Levels

## Required Files

### Level

* Clue - The initial image to displayed for the level
* Hint[1-4] - The images to displayed
* Answered by - Select all answers that lead to this level.

### Answer

* Name - The name that will displayed on any Level answered by this answer
* Description - A text file for the description that will displayed on any Level answered by this answer
* Info - A JSON file containing a single dictionary with the following parameters
** latitude - The latitude of the location of this answer
** longitude - The longitude of the location of this answer
** tolerance - How near to this answer, in metres, a team must guess for it to be correct.

## Uploading Levels and Answers
- Navigate to \<domain\>/mgmt
- Create an initial level, with the name and description of what you wish to appear at the start of the hunt.
- Upload levels 1-N of the hunt, 
- Upload a dummy level N+1 using the dummy level files - replace clue with an image for the final page
- Navigate to \<domain\>/home and check your level(s) display correctly

# Starting the Hunt

- Add a User object via \<domain\>/admin
- Add a HuntInfo object for each user with default values
- Create a UserLevel object for each user, linking the hunt to the first Level, set the Hints shown to 1.
- Pass the username and password to the teams and they can begin the hunt!