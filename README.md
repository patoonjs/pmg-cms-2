Parliamentary Monitoring Group website
======================================

Parliamentary monitoring application for use by the Parliamentary Monitoring Group in Cape Town, South Africa.
See: https://www.pmg.org.za.

## What does this project do

Allow citizens and other interested parties to monitor what's going on in the South African parliament. With specific
focus on tracking the progress of legislation as it moves through the various phases: from being introduced for the
first time to finally being approved and signed into law.

The purpose of the project is to improve parliamentary oversight, make the parliamentary process more accessible
and improve transparency surrounding the activities of parliament.

## How it works

The project consists of the following major components:

  * User-facing website, including free and paid-for content (built using Flask, Jinja2 templates, Bootstrap and jQuery)
    * https://pmg.org.za
  * Database (PostgreSQL)
  * Search engine (Elastic Search)
  * Admin interface (Flask-Admin, integration with Mandrill for email notifications)
    * https://pmg.org.za/admin
  * API (Flask)
    * https://api.pmg.org.za
    * When this web app connects to its own API, it always  connects to 127.0.0.1:5000 and sends the Host header of the `api.` subdomain of `SERVER_HOST` to avoid routing "dogfooding" traffic to the outside internet.

## Making use of the API

All of the data that is displayed through the frontend website, is served
through an API at https://api.pmg.org.za which is freely accessible.  However,
please note that access to some content on the frontend website is restricted,
and the same restrictions apply for the API.

* [More details on the API and what it contains are in API.md](API.md)

## Contributing to the project

This project is open-source, and anyone is welcome to contribute. If you just want to make us aware of a bug / make
a feature request, then please add a new GitHub Issue (if a similar one does not already exist).

**NOTE:** On 2015-07-05 we removed some very large files from the repo and its history, reducing the size of the repo from over 100MB to 30MB.
This required re-writing the history of the repo. You **must** [pull and rebase your changes](https://www.kernel.org/pub/software/scm/git/docs/git-rebase.html#_recovering_from_upstream_rebase).

If you want to contribute to the code, please fork the repository, make your changes, and create a pull request.

### Local setup
Build the necessary services:

    docker-compose build

Setup the database:

    docker-compose run --rm web python setup_dev_database.py
    docker-compose run --rm web python app.py db stamp head
    docker-compose run --rm web python bin/search.py --reindex all

Add the following lines to your .hosts file:

    127.0.0.1 pmg.test
    127.0.0.1 api.pmg.test

Start the server:

    docker-compose up

You should now see it running at [http://pmg.test:5000/](http://pmg.test:5000/) and [http://api.pmg.test:5000/](http://api.pmg.test:5000/).

You can login with:

    user : admin
    password : admin

Each time you pull in changes that might contain database changes:

    docker-compose run --rm web python app.py db migrate
    docker-compose run --rm web python app.py db upgrade

To delete the database for a completely fresh setup, run:

    docker-compose down --volumes

### Developing email features

Run [a local mock SMTP server](http://nilhcem.com/FakeSMTP/index.html) on port 2525

Set the SMTP environment variables

```
source env.localmail
```

### Running tests

    docker-compose -f docker-compose.yml -f docker-compose-test.yml run --rm web nosetests tests

### Deployment instructions

Deployment is to dokku, a Heroku-like environment. To deploy, simply push to the git remote:

    git push dokku

Sensitive or environment-specific configuration variables are set as environment variables using `dokku config:set`, the important ones are:

* SERVER_NAME - Flask uses this as the base hostname and port for the server - Flask Blueprint subdomains base from this. If it can't match the Host header in requests to this, it serves a 404 response.
  - `pmg.org.za` in production
  - `pmg.test:5000` in development
  - Flask seems to use this for generating absolute URLs, except when the `X-Forwarded-Host` header is provided, in which case that hostname is used for absolute URLs.
* FRONTEND_HOST - It's not currently clear if this is used anywhere
  - `https://pmg.org.za/` in production
  - `http://pmg.test:5000/` in development
* SESSION_COOKIE_DOMAIN
  - `pmg.org.za` in production
  - `pmg.test` in dev
* SQLALCHEMY_DATABASE_URI
* FLASK_ENV=production
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* SENDGRID_API_KEY
* MAIL_PASSWORD
* SECURITY_PASSWORD_SALT
* RUN_PERIODIC_TASKS=true
* SOUNDCLOUD_APP_KEY_ID
* SOUNDCLOUD_APP_KEY_SECRET
* SOUNDCLOUD_USERNAME
* SOUNDCLOUD_PASSWORD
* SOUNDCLOUD_PERIOD_MINUTES=5
* MAX_SOUNDCLOUD_BATCH=10


### Reindexing for Search

To re-index all content for search, run:

    ssh dokku@dokku.code4sa.org run python bin/search.py --reindex all

This isn't normally necessary as the search index is updated as items are created, updated and deleted.
It can be useful when the index has become out of date. Search functionality will fail while the indexing
is in progress. Re-indexing takes about 10 minutes.

### Database migration

We use [Flask-Migrate](https://flask-migrate.readthedocs.org/en/latest/) and [Alembic](https://alembic.readthedocs.org/en/latest/) for applying changes to the data model. To setup a migration script:

    python app.py db migrate -m "<revision description>"

Then to run the script on your local machine:

    python app.py db upgrade

### Updating parliamentary days

PMG needs to know the individual days in which Parliament sat, for each year. It uses this information
to calculate the number of parliamentary days that it took for bills to be adopted. It reads these days
from the file `data/parliament-sitting-days.txt`.

Updating this information is a two-step process:

1. Update the spreadsheet `data/parliament-sitting-days.xlsx` that lists the days parliament sits
2. Run `python bin/load_parliamentary_days --pm-days data/parliament-sitting-days.xlsx` to update `data/parliament-sitting-days.txt`
3. Run `git diff` to sanity check the changes
3. Commit the changes

### Caching

Application-level caching is used for certain views, initially based on which views the server spends most time on as seen in NewRelic Transaction overview.

To add caching to a view, add the following decorator - it must be the decorator closest to the view method so that it caches the view result, and not the result from other decorators:

```python
from pmg import cache, cache_key, should_skip_cache
...
@cache.memoize(make_name=lambda fname: cache_key(request),
               unless=lambda: should_skip_cache(request, current_user))
```

Arguments:

- `unless` must be true when the cache should ***not*** be used. Frontend (views.py) views must always use this because the view shows them as logged in, even on pages where the rest of the data is the same. API views that don't serve subscription data or have any user-specific data don't need it.
- `make_name` must be the cache key for the view. It's very important that query strings are taken into consideration for the cache key.
