**IMPORTANT - PLEASE NOTE**

**It is your responsibility to ensure that any accounts and credentials used by
this app are set up with adequate security measures and usage caps, such that if
they are compromised, no charges or problems will arise.**

You can check where a given credential is used by searching the code for the
name of the environment variable that holds it (see Setup below).

Due to the the terms of certain dependencies, this application may **not** be
used to generate revenue.

---

# Deploying the app

You can either deploy this app hosted (on Heroku) or locally.

If you are deploying on Heroku you will need a Dropbox account, with an app set
up with read/write permission to a specific folder to hold the level images, and
a corresponding OAuth key.
See <https://www.dropbox.com/developers/apps>.

If you are using Google Maps you will need a Google Cloud account with Places
and Maps JavaScript APIs enabled, and an API key.

- See <https://console.cloud.google.com/apis/dashboard>.
- NOTE: this API key is passed to clients, so you must ensure you have
  appropriate usage limits configured to avoid being charged if it is
  mis-used. You may also wish to employ additional security measures e.g.
  configuring an allowed redirect URI.

## How to deploy using Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed

### Setup

- Create your Heroku app
- Set the `DJ_KEY` environment variable to a secret string
- Set the `DB_TOKEN` environment variable to your DropBox OAuth token
- If you are using Google Maps: Set the `GM_API_KEY` environment variable to your
  Google API key
- Set the `APP_URL` environment variable to the root domain for your app (e.g.
  example.com)
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

## How to deploy locally

To save on dependency-chasing, a Dockerfile is provided.
Build the image:

```
docker build --tag e-treasure-hunt .
```

Collect static files (you should re-run this if you change the templates):

```
docker run \
  --user "$EUID":"${GROUPS[0]}" \
  --rm \
  --mount type=bind,source=$PWD,target=/usr/src/app \
  e-treasure-hunt collectstatic --no-input
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
browser at <https://localhost:80>.

```
docker run \
  --user "$EUID":"${GROUPS[0]}" \
  --rm \
  --mount type=bind,source=$PWD,target=/usr/src/app \
  --publish 80:8000 \
  e-treasure-hunt
```

To use Google maps, you will also need to pass `GM_API_KEY` to this container as
an environment variable.

# Initiating the app

## Admin initiation

- Navigate to <domain>/admin
- Create an AppSetting object - tick "active"
  - Here you can force use of the alternate map

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

## Level upload

- Navigate to <domain>/mgmt
- Upload a dummy level 0 using the dummy level files - replace blurb.txt and the
  level name in about.json with text for the start of the hunt
- Upload levels 1-N of the hunt
- Upload a dummy level N+1 using the dummy level files - replace clue with an
  image for the final page
- Navigate to <domain>/home and check your level(s) display correctly

## Create users

- Add a User object via <domain>/admin
- Pass the username and password to the teams and they can begin the hunt!
