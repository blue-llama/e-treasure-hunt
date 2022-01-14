**IMPORTANT - PLEASE NOTE**

**It is your responsibility to ensure that any accounts and credentials used by
this app are set up with adequate security measures and usage caps, such that if
they are compromised, no charges or problems will arise.**

You can check where a given credential is used by searching the code for the
name of the environment variable that holds it.

Due to the terms of certain dependencies, this application may not be used to
generate revenue.

---

# Deploying the app

You can either deploy this app hosted (on Heroku) or locally.

Either way, you will need an [ArcGIS for Developers
account](https://developers.arcgis.com/en/plans) and API key.
This is a [condition of
use](https://github.com/Esri/esri-leaflet-geocoder#terms-and-conditions) of the
esri-leaflet-geocoder project; see also the ArcGIS website.

If you are using Google Maps you will need a Google Cloud account with Places
and Maps JavaScript APIs enabled, and an API key.
See <https://console.cloud.google.com/apis/dashboard>.

NOTE: these API key are passed to clients, so you must ensure you have
appropriate usage limits configured to avoid being charged in case of mis-use.
You may also wish to employ additional security measures e.g. configuring an
allowed redirect URI.

## How to deploy locally

To save on dependency-chasing, a Dockerfile is provided.
Build the image:

```
docker build --tag e-treasure-hunt .
```

Run database migrations and create the admin user:

```
docker run \
  --user "$EUID":"${GROUPS[0]}" \
  --rm \
  --mount type=bind,source=$PWD,target=/usr/src/app \
  e-treasure-hunt migrate

docker run \
  --user "$EUID":"${GROUPS[0]}" \
  --interactive \
  --tty \
  --rm \
  --mount type=bind,source=$PWD,target=/usr/src/app \
  e-treasure-hunt createsuperuser
```

With this setup done you can run the app as below, and should find it in your
browser at <http://localhost:8000>.

```
export ARCGIS_API_KEY=<your API key>
docker run \
  --env ARCGIS_API_KEY \
  --user "$EUID":"${GROUPS[0]}" \
  --rm \
  --mount type=bind,source=$PWD,target=/usr/src/app \
  --publish 8000:8000 \
  e-treasure-hunt
```

To use Google maps, you will also need to pass `GM_API_KEY` to this container as
an environment variable.

## How to deploy using Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed
- Dropbox account
  - an app set up with read/write permission to a specific folder (to hold
    images), and a corresponding OAuth key.
  - See <https://www.dropbox.com/developers/apps>.

### Setup

- Create your Heroku app
- Set the `DEPLOYMENT` environment variable to `HEROKU`
- Set the `SECRET_KEY` environment variable to a secret string
- Set the `DROPBOX_OAUTH2_TOKEN` environment variable to your DropBox OAuth token
- Set the `ARCGIS_API_KEY` environment variable to your ArcGIS API key
- If you are using Google Maps: Set the `GM_API_KEY` environment variable to your
  Google API key
- Set the `APP_URL` environment variable to the root domain for your app (e.g.
  `e-treasure-hunt.herokuapp.com`)
- Add a Heroku Postgres add-on to your app

### Deploy

- Deploy the app to Heroku
- Use the CLI to run `heroku run -a <app_name> python manage.py createsuperuser`
  and set up an admin user

### Other useful heroku commands

Commands that I have previously searched for, dumped here to jog the memory
later.

- `heroku git:remote -a <app_name>`
- `heroku maintenance:on` and `heroku maintenance:off`
- `heroku ps:scale web=0` and `heroku ps:scale web=1`
- `heroku pg:reset`
- `heroku logs --tail -a <app_name>`

# Initiating the app

## Create levels

- You can use the content of `dummy_files.zip` as a template
- `about.json` contains the name and location for the level (the name is displayed
  on the _next_ level page, so can be the location) - tolerance is in meters
- `blurb.txt` contains the description for the level (displayed on the next level
  page)
- `clue.png` is the first image - the dummy file contains a background
- `hint1.png`-`hint4.png` are the hints, in order
  - The five images must be in alphabetical order, but otherwise the exact
    filenames are not important
  - `.png` and `.jpg` are acceptable formats

## Level upload

Levels can be uploaded either through a REST API, or via the UI.
The REST API gives better error messages when things go wrong.

### Level upload through the API

[upload.py](upload.py) contains utilities for uploading levels and hints.

You'll need to update the `PASSWORD` at the top of the file, and then re-arrange
`main()` as needed to upload your levels.

### Level upload through the UI

- Navigate to <domain>/mgmt
- Upload a dummy level 0 using the dummy level files - replace blurb.txt and the
  level name in about.json with text for the start of the hunt
- Upload levels 1-N of the hunt
- Upload a dummy level N+1 using the dummy level files - replace clue with an
  image for the final page
- Navigate to <domain>/home and check your level(s) display correctly

### Troubleshooting

The server is not very helpful if you don't get things just right, especially
via the UI.

- You really do need to upload both the dummy levels 0 and N+1
- If level upload is failing:
  - Make sure that you are uploading exactly one `.txt` file, one `.json` file
    and five images
  - Make sure that the contents of the JSON file describing the level match the
    example `about.json`

## Create users

- Add a User object via <domain>/admin
- Pass the username and password to the teams and they can begin the hunt!
