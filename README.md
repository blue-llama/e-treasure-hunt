# Setup

You will need:
=======
| **IMPORTANT - PLEASE NOTE** |
| --- |
| **It is your responsibility to ensure that any accounts and credentials used by this app are set up with adequate security measures and usage caps, such that if they are compromised, no charges or problems will arise.** You can check where a given credential is used by searching the code for the name of the environment variable that holds it (see Setup below). |
| Due to the the terms of certain dependencies, this application may **not** be used to generate revenue. |

-----

# Ways to run
You can either run this app hosted (on Heroku) or locally. 
The `local-run` branch should generally be up-to-date with master, and contain the necessary changes to allow you to host the app locally without a Heroku account. See the README in that branch for instructions on how to do this.

You do not need to use Google Maps. If you choose not to, an alternate map is available which uses Leaflet and OpenStreetMap.

# How to deploy using Heroku
## Prerequisites
- Dropbox account, with an app set up with read/write permission to a specific folder to hold the level images, and a corresponding OAuth key
- Free [ArcGIS for Developers account](https://developers.arcgis.com/en/plans) - if your application will generate more than 1,000,000 requests per month against ArcGIS APIs then you may require a paid subscription instead
- If you are using Google Maps: Google Cloud account with Places and Maps JavaScript APIs enabled, and API key - ***NOTE: this API key is passed to clients, so you must ensure you have appropriate usage limits configured to avoid being charged if it is mis-used. You may also wish to employ additional security measures e.g. configuring an allowed redirect URI.***
- Heroku account
- Heroku CLI installed

## Setup
- Create your Heroku app
- Set the DJ_KEY environment variable to a secret string
- Set the DB_TOKEN environment variable to your DropBox OAuth token
- If you are using Google Maps: Set the GM_API_KEY environment variable to your Google API key
- Set the APP_URL environment variable to the root domain for your app (e.g. example.com)
- Add a Heroku Postgres add-on to your app

## Deploy
- Deploy the app to Heroku
- Use the CLI to run 'heroku run -a <app_name> python manage.py createsuperuser' and set up an admin user

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

# Testing changes

Unit tests are available in the (hunt/tests/) folder. They can be run using pytest by running the command `pytest tests/`. Remember that you need to create migrations for any model changes that you make `python manage.py makemigrations hunt` and then migrate the database `pythong manage.py migrate` before running the tests.

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