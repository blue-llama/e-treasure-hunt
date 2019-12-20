You will need:
- Heroku account
- Dropbox account, with an app set up with read/write permission to a folder to hold the images, and an OAuth key
- Google Cloud account with maps APIs enabled, and API key
- Heroku CLI installed

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
- Create a HuntInfo object for the admin user - set hints displayed to 5
- Create an AppSetting object - tick "active" and set next hint release to now
- Create HintTime objects for all required hint release windows

Create levels:
- You can use the content of dummy_files.zip as a template
- about.json contains the name and location for the level (the name is displayed on the *next* level page, so can be the location) - tolerance is in meters
- blurb.txt contains the description for the level (displayed on the next level page)
- clue.png is the first image - the dummy file contains a background
- hint1.png-hint4.png are the hints, in order - you can use the background from the clue file

Level upload:
- Navigate to <domain>/mgmt
- Upload a dummy level 0 using the dummy level files - replace blurb.txt and the level name in about.json with text for the start of the hunt
- Upload levels 1-N of the hunt
- Upload a dummy level N+1 using the dummy level files - replace clue with an image for the final page
- Navigate to <domain>/home and check your level(s) display correctly

Create users:
- Add a User object via <domain>/admin
- Add a HuntInfo object for each user with default values
- Pass the username and password to the teams and they can begin the hunt!