| **IMPORTANT - PLEASE NOTE** |
| --- |
| **It is your responsibility to ensure that any accounts and credentials used by this app are set up with adequate security measures and usage caps, such that no unexpected charges or other problems will arise.** You can check where a given credential is used by searching the code for the name of the environment variable that holds it (see Setup below). |
| Due to the the terms of certain dependencies, this application may **not** be used to generate revenue. |

-----

# Ways to run
You can either run this app hosted (on Heroku) or locally. 
The `local-run` branch should generally be up-to-date with master, and contain the necessary changes to allow you to host the app locally without a Heroku account. See the README in that branch for instructions on how to do this.

You do not need to use Google Maps. If you choose not to, an alternate map is available which uses Leaflet and OpenStreetMap.

# How to deploy using Heroku
## Prerequisites
- Dropbox account, with an app set up with read/write permission to a specific folder to hold the level images, and a corresponding OAuth key
- [ArcGIS for Developers account](https://developers.arcgis.com/en/plans) - this is a condition of use of the esri-leaflet-geocoder package and the underlying ArcGIS geocoding Api, used by the Alt Map. Use of this API is subject to terms and conditions, although it is currently free for low usage rates - see [Terms](https://github.com/Esri/esri-leaflet-geocoder#terms-and-conditions) and [Cost](https://github.com/Esri/esri-leaflet-geocoder#cost) in the esri-leaflet-geocoder project, as well as the ArcGIS website. 
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

## Initiating the app
### Admin initiation
- Navigate to <domain>/admin
- Create a HuntInfo object for the admin user - set hints displayed to 5
- Create an AppSetting object - tick "active" and set next hint release to now; if you are NOT using Google Maps, tick "use alternate map"
- Create HintTime objects for all required hint release windows

### Create levels
- You can use the content of dummy_files.zip as a template
- about.json contains the name and location for the level (the name is displayed on the *next* level page, so can be the location) - tolerance is in meters
- blurb.txt contains the description for the level (displayed on the next level page)
- clue.png is the first image - the dummy file contains a background
- hint1.png-hint4.png are the hints, in order - you can use the background from the clue file

### Level upload
- Navigate to <domain>/mgmt
- Upload a dummy level 0 using the dummy level files - replace blurb.txt and the level name in about.json with text for the start of the hunt
- Upload levels 1-N of the hunt
- Upload a dummy level N+1 using the dummy level files - replace clue with an image for the final page
- Navigate to <domain>/home and check your level(s) display correctly

### Create users
- Add a User object via <domain>/admin
- Add a HuntInfo object for each user with default values
- Pass the username and password to the teams and they can begin the hunt!
